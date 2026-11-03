# frontend

SvelteKit 3 + TypeScript + Tailwind CSS 4, built with Vite.

## Setup

```bash
pnpm install
cp .env.example .env  # Set API_URL to the running Flask backend (default :5000)
pnpm dev        # http://localhost:5173
```

`API_URL` is server-only and excludes the `/api` suffix. For example:
`API_URL=http://127.0.0.1:5000`. If Flask uses port 5001, change this value to
`http://127.0.0.1:5001` too. The browser submits to SvelteKit, server-side code in
`src/lib/server/api.ts` calls Flask.

`SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` are server-only too. `src/hooks.server.ts`
builds a per-request Supabase client with `@supabase/ssr` that keeps the session in
httpOnly cookies, renews it when the access token expires, and exposes it as
`locals.session`. The browser never holds tokens: the server forwards the access
token to Flask as `Authorization: Bearer …`. The Supabase **secret** key belongs to
the backend only.

## Scripts

| Command        | Description                  |
| -------------- | ---------------------------- |
| `pnpm dev`     | Dev server on :5173          |
| `pnpm build`   | Production build             |
| `pnpm preview` | Preview the production build |
| `pnpm check`   | Type-check (`svelte-check`)  |

## Structure

```
src/
├── app.css               # Tailwind entrypoint (@import 'tailwindcss')
├── app.d.ts              # App.Locals / App.PageData typings
├── app.html              # HTML shell
├── hooks.server.ts       # Per-request Supabase client, session on locals
├── lib/                  # Imported via the `#lib` alias
│   ├── assets/favicon.svg
│   ├── components/       # PoolForm, PoolCard, StatusBadge
│   ├── server/api.ts     # Server-to-server Flask calls
│   ├── server/session.ts # endSession(): log this browser out (logout, Flask 401)
│   ├── redirect.ts       # loginPath() and sameSitePath(): only same-site `redirectTo` targets
│   ├── types.ts
│   └── index.ts
└── routes/
    ├── +layout.svelte    # Imports app.css, header with the User's name / Log out, or Log in / Sign up
    ├── +layout.server.ts # Loads the current User from GET /api/me
    ├── +page.svelte        # Pool listing
    ├── +page.server.ts     # Loads pools from Flask
    ├── signup/             # Sign-up page and server action
    ├── login/              # Login page and server action (`?redirectTo=` support)
    ├── logout/             # POST-only action: signs out, redirects home
    └── pools/new/          # Creation page and server action (login required)
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
	--color-brand-500: oklch(0.72 0.15 250);
	--font-display: 'Inter', sans-serif;
}
```

That generates `bg-brand-500`, `font-display`, and so on. See the
[Tailwind v4 docs](https://tailwindcss.com/docs) for details.

## Adding routes

Create a folder under `src/routes/` with a `+page.svelte`:

```
src/routes/about/+page.svelte   →  /about
```

Data loading (`+page.server.ts`), form actions, endpoints (`+server.ts`) and
layouts all work as usual. See the [SvelteKit docs](https://svelte.dev/docs/kit).

## SvelteKit 3 notes

This project is on SvelteKit 3, which differs from v2 in a couple of ways:

- The lib alias is **`#lib/...`** (not `$lib/...`), and imports include the
  **file extension**, e.g. `#lib/assets/favicon.svg`.
- Config lives in **`vite.config.ts`** — there is no `svelte.config.js`.
- Environment variables (when you need them) are declared in `src/env.ts` and
  imported from `$app/env/public` or `$app/env/private`.

## Deploying

`vite.config.ts` uses `@sveltejs/adapter-cloudflare`. GitHub Actions deploys the
production Worker from `main` and the staging Worker from `staging`.
`wrangler.jsonc` defines a server-only `API_URL` for each environment, pointing
to the corresponding Flask service on Render, plus `SUPABASE_URL` and
`SUPABASE_PUBLISHABLE_KEY` (the same Supabase project for every environment).

See the root [deployment instructions](../README.md#environments) for environment
URLs and repository configuration.
