# Report frontend coverage in CI

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills.
- **Outcome:** Coverage in [`frontend-ci.yml`](../../../../.github/workflows/frontend-ci.yml) and the `test.coverage` block of [`frontend/vite.config.ts`](../../../../frontend/vite.config.ts), for [#202](https://github.com/MESW-LES-2627/les-project-group-8/issues/202), stacked on [PR #206](https://github.com/MESW-LES-2627/les-project-group-8/pull/206).
- **Delegated:** Added `@vitest/coverage-v8`, limited coverage to `src/lib/*.ts` and `src/env.ts` minus `types.ts` and `index.ts` (Q1, Q4, Q10 of the [grilling record](../../../assets/iterations/3/grilling-testing-policy-and-coverage.md)), wrote the per-file text table to the job summary, uploaded the HTML report as an artifact, and updated [i03.d004](../i03.d004-testing.md).
- **How we checked:** `pnpm test --coverage` locally: 36 passed; the table lists `env.ts`, `form.ts`, `format.ts`, `pool.ts`, `redirect.ts` and `account.ts` (0%, the expected gap). A deliberately failing test still writes the coverage table (`reportOnFailure`). `pnpm check` clean; the lockfile installs with CI's pnpm 12.6.0. The job summary and artifact were not seen in a real CI run before the commit.
- **Notes:** The job summary table is Istanbul's text table in a code block, since Vitest has no Markdown coverage reporter.
