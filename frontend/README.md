# frontend

SvelteKit 3 + Svelte 5 + TypeScript + Tailwind CSS 4, built with Vite.

## Requirements

- Node 22+
- [pnpm](https://pnpm.io/)

## Setup

```bash
cp .env.example .env   # API_URL=http://127.0.0.1:5000
pnpm install
pnpm dev        # http://localhost:5173
```

## Scripts

| Command           | Description                       |
| ----------------- | --------------------------------- |
| `pnpm dev`        | Start the dev server on `:5173`   |
| `pnpm build`      | Production build                  |
| `pnpm preview`    | Preview the production build      |
| `pnpm check`      | Type-check (`svelte-check`)       |
| `pnpm deploy`     | Build and deploy to Cloudflare    |
| `pnpm cf-typegen` | Generate Cloudflare binding types |

## Structure

```
src/
├── app.css               # Tailwind entrypoint (@import 'tailwindcss')
├── app.d.ts              # App.Locals / App.PageData typings
├── app.html              # HTML shell
├── env.ts                # Private/public environment variable definitions
├── lib/                  # Imported via the `#lib` alias
│   ├── assets/favicon.svg
│   ├── components/PoolCard.svelte
│   ├── server/api.ts     # Backend API proxy helper
│   ├── types.ts          # Shared TypeScript contract types
│   └── index.ts
└── routes/
    ├── +layout.svelte    # Imports app.css
    ├── +page.server.ts   # Server-side data load & actions
    └── +page.svelte
```

## Styling with Tailwind

Tailwind v4 is wired in through the `@tailwindcss/vite` plugin (see
`vite.config.ts`) and loaded once from `src/app.css`:

```css
@import 'tailwindcss';
```

`+layout.svelte` imports that file, so utility classes are available in every
route. There is **no `tailwind.config.js`** — v4 scans your source
automatically.

### Plugins

The official plugins are installed and registered with `@plugin` in
`src/app.css`:

```css
@plugin '@tailwindcss/forms';
@plugin '@tailwindcss/typography';
```

- **`@tailwindcss/forms`** — resets form controls to a consistent baseline, so
  `<input>`, `<select>` and `<textarea>` look sane without extra classes.
- **`@tailwindcss/typography`** — adds the `prose` classes for styling
  rendered HTML (Markdown, CMS content, etc.):
  `<article class="prose prose-slate">…</article>`.

### Customising the theme

To customise the theme, add an `@theme` block to `src/app.css`:

```css
@import 'tailwindcss';

@theme {
	--color-svelte: #ff3e00;
	--color-svelte-hover: #ea3600;
}
```

See the [Tailwind v4 docs](https://tailwindcss.com/docs) for details.

## Adding routes

Create a folder under `src/routes/` with a `+page.svelte`:

```
src/routes/about/+page.svelte   →  /about
```

Data loading (`+page.server.ts`), form actions, endpoints (`+server.ts`) and
layouts all work as usual. See the [Svelte docs](https://svelte.dev/docs/kit).

## SvelteKit 3 notes

This project runs SvelteKit 3 with Svelte 5:

- The lib alias is **`#lib/...`** (not `$lib/...`), and imports include the
  **file extension**, e.g. `#lib/assets/favicon.svg`.
- Config lives in **`vite.config.ts`** — there is no `svelte.config.js`.
- Environment variables are declared in `src/env.ts` and
  imported from `$app/env/public` or `$app/env/private`.

## Deploying

`vite.config.ts` uses `@sveltejs/adapter-cloudflare` to bundle the application
as a Cloudflare Worker (handling static assets + SSR at the edge). Config lives in
`wrangler.jsonc`.

### Manual deploys

Log in to Cloudflare once, then deploy:

```bash
npx wrangler login
pnpm deploy     # vite build && wrangler deploy
```

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

Staging-only config (for example `API_URL`) goes under `env.staging` in
`wrangler.jsonc`. Wrangler environments inherit `main`, `assets` and
`compatibility_*`, but **not** `vars` or bindings.

> Pushing that only *creates* a branch at an existing commit produces no file
> diff, so path-filtered workflows are skipped. Use **Actions → Run workflow**
> for the first deploy of a new environment.

