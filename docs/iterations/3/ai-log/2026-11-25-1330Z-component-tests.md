# Component tests in Vitest browser mode

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills from Matt Pocock's Skills For Real Engineers.
- **Outcome:** [#120](https://github.com/MESW-LES-2627/les-project-group-8/issues/120): `server` and `client` Vitest projects in `frontend/vite.config.ts`, a `*.svelte.test.ts` file for every component with a branch, Chromium in Frontend CI, components measured in coverage, and the [testing policy](../i03.d004-testing.md#component-tests) updated.
- **Delegated:** Added `@vitest/browser-playwright` and `vitest-browser-svelte`, split the config, wrote the tests (mocking `page` from `$app/state`, and `enhance`/`invalidateAll` through `form-actions.mock.ts` to test the submitting state), edited CI, d004 and the frontend README; ran a two-axis review (standards, spec) with sub-agents and applied its findings.
- **Where it was wrong:** Its first render calls were not awaited (`vitest-browser-svelte` 3 returns a promise), it assumed `toHaveTextContent` matched substrings, and it called `PoolCard` and `StatusBadge` display-only though both branch; the review caught the last one, and `PoolCard.svelte.test.ts` was added before committing.
- **How we checked:** `pnpm check`, `pnpm build` and `pnpm test --coverage` locally (87 tests; every component measured); the spec reviewer re-ran the suite.
- **Notes:** The issue listed six components; `BetPicks` and `PoolCard` also match its rule, so they got tests too. Uncovered: a few `BetCard` branches (a dropdown with no saved pick). Not run in CI yet.
