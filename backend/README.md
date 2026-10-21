# backend

## Requirements

- Python 3

## Setup

```bash
cd backend
cp .env.example .env   # fill in SUPABASE_URL / SUPABASE_KEY (service_role)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
flask run       # http://127.0.0.1:5000/api/health
pytest          # no Supabase needed: tests use an in-memory repository
```

### Database

Run `backend/migrations/001_init.sql` in the Supabase SQL Editor. It creates
the `users`, `pools`, `outcomes`, and `picks` tables and seeds the guest user.
No ORM is used (DOO requirement): queries go directly through `supabase-py`.


## Deploying the backend (Render)

`render.yaml` is a Render Blueprint defining two free web services:

| Environment | Branch    | Service               | URL |
| ----------- | --------- | --------------------- | --- |
| Production  | `main`    | `les-backend`         | https://les-backend.onrender.com |
| Staging     | `staging` | `les-backend-staging` | https://les-backend-staging.onrender.com |

One-time setup: Render Dashboard → **New → Blueprint** → select this repo,
then set `SUPABASE_URL` and `SUPABASE_KEY` for each service. If Render assigns
a different URL (name taken), update `vars.API_URL` in `frontend/wrangler.jsonc`.

Pushes that touch `backend/` deploy automatically once **Backend CI**
(`.github/workflows/backend-ci.yml`) passes. Free instances sleep after 15
minutes idle, so the first request can take ~30s; the frontend streams the
pool list so the page still renders immediately.

## Deploying the frontend

The frontend is deployed to Cloudflare Workers using `@sveltejs/adapter-cloudflare`.

For manual deployment steps, GitHub Actions secrets, staging/production environments, and Wrangler configuration, see [frontend/README.md](frontend/README.md#deploying).

### Structure

```
backend/
├── app.py                  # Entry point: routes, Supabase queries, in-memory store
├── migrations/             # SQL migrations (001_init.sql)
├── tests/                  # pytest suite (in-memory repository)
├── requirements.txt
└── requirements-dev.txt
render.yaml                 # Render Blueprint (backend prod + staging)
```

