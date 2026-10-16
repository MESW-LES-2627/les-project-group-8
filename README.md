# LES

A SvelteKit 3 app with TypeScript and Vite.

## Requirements

- Node 22+
- [pnpm](https://pnpm.io/)

## Getting started

```bash
cd frontend
pnpm install
pnpm dev        # http://localhost:5173
```

## Scripts

| Command        | Description                  |
| -------------- | ---------------------------- |
| `pnpm dev`     | Start the dev server         |
| `pnpm build`   | Build for production         |
| `pnpm preview` | Preview the production build |
| `pnpm check`   | Type-check with svelte-check |

## Structure

```
frontend/
├── src/
│   ├── app.d.ts            # App namespace typings
│   ├── app.html            # HTML shell
│   ├── lib/                # Imported via the `#lib` alias
│   │   ├── assets/favicon.svg
│   │   └── index.ts
│   └── routes/
│       ├── +layout.svelte
│       └── +page.svelte
├── static/                 # Served as-is at the root
├── tsconfig.json
└── vite.config.ts
```

## SvelteKit 3 notes

- The lib alias is `#lib/...` and imports include the file extension,
  e.g. `#lib/assets/favicon.svg`.
- Config lives in `vite.config.ts`; there is no `svelte.config.js`.
