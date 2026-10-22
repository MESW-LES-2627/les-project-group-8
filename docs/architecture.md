# Backend architecture

The backend is a **modular monolith**: one Flask app, one deployment, split into modules by business area. Each module has the same four files, so once you understand one module you understand all of them.

## Modules

```
backend/
├── app.py             # create_app(): builds everything and registers the routes
├── shared/            # code every module uses
│   ├── db.py          # Supabase client (refuses to start without credentials)
│   ├── errors.py      # ValidationError -> 400, NotFoundError -> 404, anything else -> 500
│   └── validation.py  # small input checks: JSON object, required text
├── users/             # people who create pools
│   ├── models.py
│   ├── service.py
│   ├── repository.py
│   └── routes.py
└── pools/             # two-option prediction pools
    ├── models.py
    ├── service.py
    ├── repository.py
    └── routes.py
```

| File | Responsibility | Knows about |
| :--- | :--- | :--- |
| `routes.py` | HTTP only: read the request, call the service, turn the result into JSON | Flask, its own service and models |
| `service.py` | Business rules: validation, defaults (decider = creator), talking to other modules | its own repository, other modules' services |
| `repository.py` | Database access with `supabase-py`. Rows are turned into dataclasses by hand | Supabase, its own models |
| `models.py` | Plain dataclasses (`User`, `Pool`, `Outcome`...), plus rules that only need the data itself (`Pool.status()`) | Python standard library |

```mermaid
flowchart LR
  App["app.py create_app"]
  subgraph usersModule [users]
    UR[routes] --> US[service] --> URepo[repository]
  end
  subgraph poolsModule [pools]
    PR[routes] --> PS[service] --> PRepo[repository]
  end
  subgraph sharedModule [shared]
    DB[db]
    ERR[errors]
    VAL[validation]
  end
  App -.builds.-> UR
  App -.builds.-> PR
  PS -->|"get_user()"| US
  URepo --> Supabase[(Supabase Postgres)]
  PRepo --> Supabase
```

## Dependency rules

1. **Inside a module, calls go one way:** `routes -> service -> repository`. A repository never calls a service, and a service never touches Flask's `request`.
2. **Cross-module business behavior goes through services.** `PoolService` asks `UserService.get_user()` to validate the creator and never imports `users.repository`. The pool repository's read projection joins `users` to obtain creator/decider summaries; that is response mapping, not cross-module service logic.
3. **`shared/` depends on no module.** Modules depend on `shared/`, never the other way around.
4. **`app.py` wires application-wide services and repositories.** Services receive their repository (and other services) through the constructor. Routes and services can still construct request-scoped model objects. Constructor injection lets tests swap the database for a fake.

## Iteration 0 demonstration

The canonical scope is [MVP: Thin Vertical Slice](iterations/0/i00.d002-mvp.md#thin-vertical-slice-iteration-0).
For that journey, the frontend sends the pre-seeded Guest User's `creator_id`.
`PoolService` validates the user and sets the decider to the creator. The
`POST /api/users` capability is available and tested, but no user-creation screen
is required for the guest-based demonstration. `/api/health` checks Flask
availability only; database persistence needs a separate create/list check.

## Request flow: creating a pool

```mermaid
sequenceDiagram
  participant Client
  participant Routes as pools/routes.py
  participant Service as pools/service.py
  participant Users as users/service.py
  participant Repo as pools/repository.py
  participant DB as Supabase

  Client->>Routes: POST /api/pools {creator_id, name, ...}
  Routes->>Service: create_pool(payload)
  Service->>Users: get_user(creator_id)
  Users-->>Service: User (or NotFoundError -> 400)
  Service->>Service: parse_new_pool() validates fields -> NewPool
  Service->>Repo: create_pool(new_pool)
  Repo->>DB: insert pool, insert 2 outcomes, select pool
  DB-->>Repo: row
  Repo-->>Service: Pool
  Service-->>Routes: Pool
  Routes-->>Client: 201 JSON (status computed by Pool.status())
```

If any step raises `ValidationError` or `NotFoundError`, the error handlers in `shared/errors.py` turn it into a JSON response. Any other exception becomes a generic `500 {"error": "Internal server error."}`, and the details are only logged.

## Patterns, and where to find them

| Pattern | Where | Why |
| :--- | :--- | :--- |
| Layered modules (modular monolith) | `users/`, `pools/` | Each business area can grow on its own without a distributed system |
| Repository | `*/repository.py` | Services don't know how or where data is stored |
| Manual row mapping (Data Mapper idea, no ORM) | `_to_pool()` in `pools/repository.py` | The class forbids ORMs; mapping by hand keeps the SQL/table shape out of the models |
| Dependency injection (by constructor) | `create_app()` in `app.py` | Tests pass fake repositories, and production passes Supabase ones. No framework needed |
| Application factory | `create_app()` | Each test gets a fresh app; Gunicorn calls `app:create_app()` |
| Test double (fake) | `tests/fakes.py` | Acceptance tests run without a database (see [testing](iterations/0/i00.d004-testing.md)) |

## Decisions and tradeoffs

### 1. A modular monolith, not MVC or microservices

- **Chosen:** one app, split into modules by business area (`users`, `pools`).
- **Why:** a flat "all routes in one file" layout mixed HTTP, rules and SQL in the same functions. Microservices would add network calls and deployments for a three-endpoint app.
- **Cost:** module boundaries are a convention (rule 2 above), not enforced by the language. We keep them in code review.

### 2. Keep `supabase-py` instead of raw SQL with `psycopg`

- **Chosen:** `supabase-py`, which calls Supabase's REST API. It is a query builder, not an ORM: there are no mapped classes, no lazy loading, and no automatic saving.
- **Why:** it was already set up on Render and needs no new secret.
- **Cost:** the current direct table requests execute separately. If the outcomes insert fails, `create_pool` attempts to delete the pool it just created. A crash or failed deletion can still leave incomplete data; this is compensating cleanup, not an atomic transaction. Atomic creation would require a separate implementation change, such as a transaction over a SQL connection or a database function. That change is deferred beyond the current implementation.

## Adding a module in a later iteration (e.g. picks)

1. Create `backend/picks/` with `models.py`, `service.py`, `repository.py`, `routes.py`.
2. `PickService` receives a `PickRepository`, plus `PoolService` and `UserService` if it needs pools or users. It never reads their tables.
3. Build it in `create_app()` and register its blueprint.
4. Add a fake to `tests/fakes.py`, write the user story with acceptance criteria, and add one acceptance test per criterion.

## Not done yet (on purpose)

- **Picks and resolving pools.** The `picks` table exists in `001_init.sql` but no code uses it yet.
- **`002_create_pool_fn.sql`** (a stored procedure for atomic pool creation) is not used by the code. See decision 2.
- **Authentication.** Any client can create users and pools, which is acceptable for the Iteration 0 prototype.
- **Outcome order.** `GET /api/pools` does not guarantee that the two outcomes come back in the order they were created.

Known contract and integration gaps from the local review are recorded in
[testing and verification limits](iterations/0/i00.d004-testing.md#review-findings-and-verification-still-required).
They must be checked separately from the architectural decisions above.

## Known configuration issue

Supabase row-level security rejects inserts (and appears to hide existing rows from reads) when `SUPABASE_KEY` is the **publishable** key. The backend must use the **`service_role`** key, both locally (`backend/.env`) and on Render. That key must never be sent to the frontend.
