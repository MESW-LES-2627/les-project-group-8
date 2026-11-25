# Grilling session: testing policy and coverage report

- **Date:** 2026-11-25 UTC.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the decisions below, to be split into tickets with `/to-tickets`.
- **Summary:** see the session entry
  [2026-11-25-1028Z-testing-policy-grilling.md](../../../iterations/3/ai-log/2026-11-25-1028Z-testing-policy-grilling.md).

This is a structured record of the session. Alef's messages are quoted word for
word. The AI's questions are shortened to their decision and its recommended
answer.

## 1. How it started

A handoff note named the biggest gap for the iteration 3 review:
[`docs/evaluation.md` §4 "Unit Tests (living)"](../../../evaluation.md#4-unit-tests-living)
is capped at 1–4 while there is "No metrics report. No testing policy."

## 2. Facts the AI looked up

- No coverage anywhere: `backend-ci.yml` runs `pytest -v`, `frontend-ci.yml`
  runs `pnpm test` (`vitest run`), no workflow publishes a report.
- The policy is not missing, it is scattered. `i03.d004-testing.md` already
  says Supabase queries, SQL constraints and migration data preservation are
  not covered by the fakes (checked on staging for #29), the JWKS fetch was
  checked by hand, and Svelte components are not unit-tested (#120). It states
  no rule.
- The backend has no unit tests in the narrow sense: all are acceptance tests
  over HTTP with in-memory repositories, plus the RLS integration test.
- The e2e stack runs the real Flask app against local Supabase, so
  `TokenVerifier.from_env` → `for_jwks` and every migration already run in CI.
  Only the JWKS caching (one fetch, one refetch on a new `kid`) was manual.
- `CLAIM.md` already links d004 as "Tests, policy and how to run".

## 3. Decisions

| # | Question | Answer |
| :- | :- | :- |
| Q1 | Form of the metrics report | Per-file coverage table in each CI run's job summary, HTML report as an artifact, and a snapshot in d004 for a stable link at the tag. Codecov/Coveralls PR comments: separate issue, to be decided ([#195](https://github.com/MESW-LES-2627/les-project-group-8/issues/195)). |
| Q2 | Metric for "logic that can break" | Line and branch coverage per module, domain services called out. Mutation testing: separate issue, to be decided ([#196](https://github.com/MESW-LES-2627/les-project-group-8/issues/196)). |
| Q3 | What counts in the denominator | See below. |
| Q4 | Coverage gate | Report only, no threshold. |
| Q5 | Where the policy lives | A **Testing policy** section in `i03.d004-testing.md`, replacing "What we test, and why": tested (by layer), not tested and why, rules. Links the metrics report. |
| Q6 | Same-PR habit | `.github/pull_request_template.md` with one checkbox: "Tests for this change are in this PR, or the policy says why not". |
| Q7 | Branch protection | Separate issue, to be decided ([#197](https://github.com/MESW-LES-2627/les-project-group-8/issues/197)). |
| Q8 | Assignees for #179–#182 | Alef, for now. Done in the session. |
| Q9 | Backend exclusions | `*/repository.py` and `shared/db.py` (covered by e2e). Everything else measured, with `--cov-branch`. |
| Q10 | Frontend exclusions | Measure `src/lib/*.ts` and `src/env.ts`. Exclude routes, `hooks.server.ts`, `lib/server/**` (e2e), components (e2e, unit tests in #120), and type-only or re-export files (`app.d.ts`, `types.ts`, `index.ts`). `account.ts` stays in and shows as a gap. |
| Q11 | Snapshot in d004 | A **Coverage** subsection: one table per layer, line and branch % per file, commit SHA and CI run. Refreshed in the PR that prepares the `iter-N` tag. |
| Q12 | Later issues | `Task`, assigned to Alef, `needs-triage`, no estimate. |
| Q13 | Automate the JWKS check | An integration test with a stdlib HTTP server that counts fetches: repeated tokens cause one fetch, a new `kid` causes one refetch. Plus a test that `from_env` without `SUPABASE_URL` raises. Ships in the same PR as the coverage work. |
| Q14 | Rule against hand checks | Every exclusion names the automated layer that covers it. A hand check is a gap with an open issue, never coverage. Today's gap: migration data preservation ([#198](https://github.com/MESW-LES-2627/les-project-group-8/issues/198)). |

### Q3: coverage respects what each layer is responsible for

The AI first recommended measuring everything, so untested Supabase code and
Svelte routes would show as near 0%. Alef pushed back:

> why not just make coverage respect what is actually being tested?

Agreed, with one condition: excluding whatever happens to be untested makes
the number circular ("100% of what we test"), which the rubric calls noise.
So the exclusion lists in the coverage configs are the policy's "not
unit-tested" list, and each entry names the automated layer that covers it.
Report and policy then agree by construction (band 8).

### Q9 and Q13: hand checks

The AI proposed leaving the JWKS methods in the report as known misses,
checked by hand. Alef:

> I think checked by hand is not a good thing, we probably should include them right?

That led to the JWKS test (Q13) and the policy rule (Q14).

## 4. Not decided here

- No glossary change: none of this is domain language.
- No ADR: every choice is cheap to reverse.
- Coverage numbers were not measured in the session.
