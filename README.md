# LES

A SvelteKit 3 frontend with TypeScript, Tailwind CSS 4 and Vite, plus a Flask
backend.

The **frontend** is built for and deployed to **Cloudflare Workers**. The
**backend** runs as a plain Flask app locally; its deployment is still to be
decided.

## Requirements

- Node 22+
- [pnpm](https://pnpm.io/)
- Python 3

## Getting started

### Frontend

```bash
cd frontend
pnpm install
pnpm dev        # http://localhost:5173
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask run       # http://127.0.0.1:5000
```

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

### Staging

A separate Worker, `les-frontend-staging`, is deployed from the `staging` branch
by `.github/workflows/deploy-staging.yml` (or manually from the **Actions** tab).
It uses the same `CLOUDFLARE_API_TOKEN` / `CLOUDFLARE_ACCOUNT_ID` secrets.

| Environment | Branch    | Worker                 |
| ----------- | --------- | ---------------------- |
| Production  | `main`    | `les-frontend`         |
| Staging     | `staging` | `les-frontend-staging` |

Staging-only config (for example `PUBLIC_API_URL`) goes under `env.staging` in
`frontend/wrangler.jsonc`. Wrangler environments inherit `main`, `assets` and
`compatibility_*`, but **not** `vars` or bindings.

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
├── app.py
└── requirements.txt
```

## SvelteKit 3 notes

- The lib alias is `#lib/...` and imports include the file extension,
  e.g. `#lib/assets/favicon.svg`.
- Config lives in `vite.config.ts`; there is no `svelte.config.js`.
