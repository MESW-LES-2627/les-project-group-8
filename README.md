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
flask run              # http://127.0.0.1:5000/api/health
pytest -v              # acceptance tests, no database needed
```

| Variable | Value |
| -------- | ----- |
| `SUPABASE_URL` | Project URL (Supabase → Project Settings → API) |
| `SUPABASE_KEY` | The **`service_role`** key. The publishable key is blocked by row-level security. Never expose it to the frontend |

The app refuses to start if either variable is missing. Endpoints are described
in [docs/iterations/0/openapi.yaml](docs/iterations/0/openapi.yaml), and tests
in [docs/iterations/0/i00.d004-testing.md](docs/iterations/0/i00.d004-testing.md).

The default local API URL is `http://127.0.0.1:5000`. If port 5000 is occupied, run `flask run --port 5001` and set
`API_URL=http://127.0.0.1:5001` in `frontend/.env`.

The first-deadline demonstration uses the pre-seeded Guest User. The frontend
should send its `creator_id` when creating a pool. See the agreed
[Iteration 0 scope](docs/iterations/0/i00.d002-mvp.md#thin-vertical-slice-iteration-0).

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
├── shared/                 # Supabase client, errors, input checks
├── users/                  # models, service, repository, routes
├── pools/                  # models, service, repository, routes
├── migrations/             # SQL run in the Supabase SQL editor
├── tests/acceptance/       # one test per user-story acceptance criterion
└── requirements.txt
```

## SvelteKit 3 notes

- The lib alias is `#lib/...` and imports include the file extension,
  e.g. `#lib/assets/favicon.svg`.
- Config lives in `vite.config.ts`; there is no `svelte.config.js`.
