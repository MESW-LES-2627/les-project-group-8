# frontend

SvelteKit 3 + TypeScript, built with Vite.

## Setup

```bash
pnpm install
pnpm dev        # http://localhost:5173
```

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
├── app.d.ts              # App.Locals / App.PageData typings
├── app.html              # HTML shell
├── lib/                  # Imported via the `#lib` alias
│   ├── assets/favicon.svg
│   └── index.ts
└── routes/
    ├── +layout.svelte
    └── +page.svelte
```

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

`vite.config.ts` uses `@sveltejs/adapter-auto`, which picks an adapter from the
deploy platform. If yours isn't auto-detected, install the matching adapter
(e.g. `@sveltejs/adapter-node`) and set it in `vite.config.ts`.
