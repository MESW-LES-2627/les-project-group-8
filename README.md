# LES

A SvelteKit 3 frontend with TypeScript, Tailwind CSS 4 and Vite, plus a Flask
backend.

The **frontend** is built for and deployed to **Cloudflare Workers**. The
**backend** is a Flask modular monolith backed by Supabase, deployed to
**Render** (`render.yaml`). See [docs/architecture.md](docs/architecture.md)
for how it is organized and why.

## Requirements

- Node 22+
- [pnpm](https://pnpm.io/)
- Python 3.13 recommended (the version used by CI and Render)

## Getting started

### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env  # API_URL must match the local flask port
pnpm dev        # http://localhost:5173
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # then fill in the values below
flask run --port 5001  # http://127.0.0.1:5001/api/health
pytest -v              # acceptance tests, no database needed
```

| Variable | Value |
| -------- | ----- |
| `SUPABASE_URL` | Project URL used to verify Supabase Auth tokens |
| `DATABASE_URL` | Server-only PostgreSQL URI from Supabase's **Connect** dialog, with the URL-encoded database password and `sslmode=require`. The database role must own the app tables or have `BYPASSRLS` |

Both variables are required. PostgreSQL stays on Supabase and login continues
through Supabase Auth. See [database setup](docs/database-setup.md) for migrations,
local PostgreSQL rollback tests and staging setup. Endpoints are described
in [docs/iterations/1/i01.d007.openapi.yaml](docs/iterations/1/i01.d007.openapi.yaml), and tests
in [docs/iterations/1/i01.d004-testing.md](docs/iterations/1/i01.d004-testing.md).

The example frontend configuration uses `API_URL=http://127.0.0.1:5001`.
Keep it aligned with Flask's port.

Creating a pool requires login: Flask makes the logged-in User its creator and
decider. The Pool starts empty with a shared deadline; its creator adds Bets
with 2–10 ordered options while it is open. Each User can save or change one
Pick per Bet before that deadline. Users are created only by
the sign-up trigger (`backend/migrations/003a_create_user_on_signup.sql`).

The #29 migration must be coordinated with the adapted backend and frontend:
local, staging and production share one database. See
[ADR 0004](docs/adr/0004-pools-contain-bets.md); applying the migration alone
breaks clients of the old schema and API. Migration
`20261105000100_pool_transactions.sql` follows it and adds one internal initial
round. The frontend still creates an empty Pool and adds Bets separately;
API callers can provide `initial_bets` to save the entire structure in one
transaction. Multiple-round management remains future scope.

## Deploying the frontend

The frontend uses `@sveltejs/adapter-cloudflare`. Log in to Cloudflare once, then
deploy:

```bash
npx wrangler login
cd frontend
pnpm deploy     # vite build && wrangler deploy
```

The Worker config lives in `frontend/wrangler.jsonc`.

### Automatic deploys (GitHub Actions)

Pushing to `main` deploys automatically via `.github/workflows/deploy.yml`. It
needs two repository secrets (Settings → Secrets and variables → Actions):

| Secret | Value |
| ------ | ----- |
| `CLOUDFLARE_API_TOKEN` | API token with **Workers Scripts: Edit** (the "Edit Cloudflare Workers" template works) |
| `CLOUDFLARE_ACCOUNT_ID` | Your account ID (Workers & Pages overview → Account Details) |

You can also run it manually from the **Actions** tab (`workflow_dispatch`).

### Environments

| Environment | Branch    | Worker                 | URL |
| ----------- | --------- | ---------------------- | --- |
| Production  | `main`    | `les-frontend`         | https://les-frontend.les-h.workers.dev |
| Staging     | `staging` | `les-frontend-staging` | https://les-frontend-staging.les-h.workers.dev |

Both deploy automatically via GitHub Actions (`.github/workflows/deploy.yml` and
`deploy-staging.yml`) and share the `CLOUDFLARE_API_TOKEN` /
`CLOUDFLARE_ACCOUNT_ID` repository secrets. Promote a change by merging
`staging` into `main`.

Staging-only config (for example the server-only `API_URL`) goes under `env.staging` in
`frontend/wrangler.jsonc`. Wrangler environments inherit `main`, `assets` and
`compatibility_*`, but **not** `vars` or bindings.

> Pushing that only *creates* a branch at an existing commit produces no file
> diff, so path-filtered workflows are skipped. Use **Actions → Run workflow**
> for the first deploy of a new environment.

## Scripts (frontend)

| Command           | Description                        |
| ----------------- | ---------------------------------- |
| `pnpm dev`        | Start the dev server               |
| `pnpm build`      | Build for production               |
| `pnpm preview`    | Preview the production build       |
| `pnpm check`      | Type-check with svelte-check       |
| `pnpm deploy`     | Build and deploy to Cloudflare     |
| `pnpm cf-typegen` | Generate Cloudflare binding types  |

## Structure

```
frontend/
├── src/
│   ├── app.css             # Tailwind entrypoint
│   ├── app.d.ts            # App namespace typings
│   ├── app.html            # HTML shell
│   ├── lib/                # Imported via the `#lib` alias
│   │   ├── assets/favicon.svg
│   │   └── index.ts
│   └── routes/
│       ├── +layout.svelte
│       └── +page.svelte
├── static/                 # Served as-is at the root
├── wrangler.jsonc          # Cloudflare Worker config (assets + SSR)
├── tsconfig.json
└── vite.config.ts          # Uses @sveltejs/adapter-cloudflare
backend/
├── app.py                  # create_app(): wires modules together
├── shared/                 # Psycopg connections, Supabase Auth, errors, input checks
├── users/                  # models, service, repository, routes
├── pools/                  # models, service, repository, routes
├── picks/                  # models, service, repository, routes
├── migrations/             # SQL run in the Supabase SQL editor; new tables need RLS on (ADR 0003)
├── tests/acceptance/       # one test per user-story acceptance criterion
└── requirements.txt
```

## SvelteKit 3 notes

- The lib alias is `#lib/...` and imports include the file extension,
  e.g. `#lib/assets/favicon.svg`.
- Config lives in `vite.config.ts`; there is no `svelte.config.js`.
