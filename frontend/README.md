# frontend

SvelteKit 3 + TypeScript + Tailwind CSS 4, built with Vite.

## Setup

```bash
pnpm install
cp .env.example .env  # Set API_URL to the running Flask backend (example :5001)
pnpm dev        # http://localhost:5173
```

`API_URL` is server-only and excludes the `/api` suffix. For example:
`API_URL=http://127.0.0.1:5001`. The browser submits to SvelteKit; server-side code in
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
| `pnpm test`    | Unit tests (Vitest)          |
| `pnpm test:e2e` | End-to-end tests (Playwright) |

## End-to-end tests

Playwright specs live in `e2e/`, apart from the Vitest unit tests, and run against a
throwaway local Supabase, never the shared project
([ADR 0005](../docs/adr/0005-e2e-tests-use-a-throwaway-local-supabase.md)).

Prerequisites:

- Docker, running.
- The [Supabase CLI](https://supabase.com/docs/guides/local-development/cli/getting-started)
  (`brew install supabase/tap/supabase`).
- The backend's dependencies in `backend/.venv` (see [Getting started](../README.md#backend)), or `flask` on your `PATH`.
- Chromium for Playwright, once: `pnpm exec playwright install chromium`.

```bash
pnpm test:e2e                 # whole suite
pnpm test:e2e e2e/signup.spec.ts --headed   # extra arguments go to `playwright test`
```

`e2e/run.sh` starts a fresh local Supabase (ES256 signing keys, email confirmation
off), applies `backend/migrations/*.sql` in sorted order, runs Playwright, and removes
the stack on exit. Playwright starts Flask on :5002 and `vite preview` on :4173, so a
dev server on :5001 or :5173 can keep running. It stops any other local Supabase
stack of this project first, so two runs can't share a machine (or worktrees) at once. Running `playwright test` directly
fails on purpose: without the local stack's URL, the frontend would fall back to the
shared project in `wrangler.jsonc`.

## Structure

Unit tests (`*.test.ts`) sit next to the module they test.

```
e2e/                      # Playwright specs and run.sh (local Supabase + Playwright)
src/
├── app.css               # Tailwind entrypoint (@import 'tailwindcss')
├── app.d.ts              # App.Locals / App.PageData typings
├── app.html              # HTML shell
├── hooks.server.ts       # Per-request Supabase client, verified session on locals
├── lib/                  # Imported via the `#lib` alias
│   ├── assets/favicon.svg
│   ├── components/       # Form, PoolForm/PoolCard, BetForm/BetCard, StatusBadge
│   ├── server/api.ts     # Server-to-server Flask calls
│   ├── server/session.ts # endSession() / clearSessionCookies(), and helpers shared by login and signup
│   ├── account.ts        # Sign-up limits (name length, password minimum)
│   ├── form.ts           # readField() and the shared form classes
│   ├── format.ts         # Deadline formatting and datetime-local conversion
│   ├── pool.ts           # validatePool() and the new-Pool limits
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
    ├── no-user/            # Where Flask's 403 lands: logged in, but the Account has no User
    ├── pools/new/          # Creates an empty Pool (login required)
    └── pools/[id]/         # Pool detail, creator's addBet action, per-Bet pick action
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
