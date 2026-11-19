# Grilling session: frontend unit tests with Vitest (issue #67)

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below for
  [#67](https://github.com/MESW-LES-2627/les-project-group-8/issues/67), and
  the follow-up
  [#120](https://github.com/MESW-LES-2627/les-project-group-8/issues/120)
  (component tests), blocked by #67.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-1205Z-vitest-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to implement 67. I want to open a stacked pr on top of 119

## 2. Facts the AI looked up

- #119 (`alef/docs-stacked-prs`) sits on #118, and
  `docs/agents/stacked-prs.md` says to start work with `gh stack add`.
- The frontend has no test runner. `frontend-ci.yml` runs `pnpm check` and
  `pnpm build` only.
- The pure code: `src/lib/format.ts`, `src/lib/redirect.ts` (`loginPath`, and
  `sameSitePath`, the open-redirect guard), `readField` in `src/lib/form.ts`,
  the URL schemas in `src/env.ts`, and `validate` in
  `src/routes/pools/new/+page.server.ts`.
- `validate` is not exported, and SvelteKit rejects unknown exports from
  `+page.server.ts`.
- [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33)
  (Playwright) is open, so there is no Playwright config yet.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Branch and stack | `gh stack add alef/issue-67-vitest` on the #119 branch; PR body "Stacked on #119" | Yes |
| Q2 | Scope | Pure functions only, Vitest `node` environment, no jsdom | Yes, for now (see below) |
| Q3 | Units | `format.ts`, `redirect.ts`, `readField`, pool `validate`, `env.ts` schemas (dropped with a reason in the PR if `defineEnvVars` doesn't expose them) | Yes |
| Q4 | Testable `validate` | Move it and `FieldErrors` to `src/lib/pool.ts`, like `account.ts` | Yes |
| Q5 | Runner config | `test` block in `vite.config.ts`; Playwright keeps its own config | Yes (see below) |
| Q6 | Test placement | `*.test.ts` next to the source | Yes |
| Q7 | Time and timezone | `vi.setSystemTime` for the future-deadline check; round-trip `toLocalInput` with `localInputToIso` instead of pinning `TZ` | Yes |
| Q8 | CI and script | `"test": "vitest run"`; a Test step after Type-check, before Build | Yes |
| Q9 | Domain docs | No glossary entries, no ADR | Yes |

On Q2 and Q5 Alef added:

> Q2 for now yes, but I want to have component tests in the codebase.

> Q5 yes, note that we want to use playwright in this iteration.

## 4. Round 2

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q10 | Component tests | A follow-up issue, blocked by #67, suggesting Vitest browser mode with the Playwright provider (`vitest-browser-svelte`) over jsdom; #67 keeps one node config | Yes, opened as #120 |
| Q11 | Keep Vitest off Playwright specs | `include: ['src/**/*.test.ts']` | Yes |
| Q12 | Testing doc | A "Frontend unit tests" section in `i02.d004-testing.md` | Yes |
| Q13 | Recording | This file, an AI-log entry, and a comment on #67 answering its open questions | Yes |

## 5. The plan

- Branch `alef/issue-67-vitest`, stacked on #119. PR body: "Closes #67.
  Stacked on #119."
- Add Vitest as a dev dependency, at a version that supports Vite 8. Add a
  `test` block to `vite.config.ts`: `environment: 'node'`,
  `include: ['src/**/*.test.ts']`.
- `package.json`: `"test": "vitest run"`.
- Move `validate` and `FieldErrors` from `pools/new/+page.server.ts` to
  `src/lib/pool.ts`; the action imports them.
- Tests next to their source:
  - `format.test.ts`: `formatDeadline` (valid, invalid ISO),
    `toLocalInput` / `localInputToIso` round trip, empty and invalid input.
  - `redirect.test.ts`: `loginPath` keeps path and query; `sameSitePath`
    rejects `https://evil.com`, `//evil.com`, `/\evil.com` and `null`, and
    keeps a same-site path with query and hash.
  - `form.test.ts`: `readField` for a string, a missing key and a file.
  - `pool.test.ts`: each `validate` error, the 120/500 limits, and a past
    deadline with the clock fixed by `vi.setSystemTime`.
  - `env.test.ts`: the URL schemas return the origin, return `undefined` when
    empty, and throw on a bad URL, if reachable through `variables`.
- `frontend-ci.yml`: a `Test` step running `pnpm test`, after Type-check.
- `i02.d004-testing.md`: a "Frontend unit tests" section mapping each test
  file to its module, and how to run them.
- Component tests and Playwright are out of scope: #120 and #33.
