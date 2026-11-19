# Grilling session: promoting staging to main

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below. Tickets come next, from `/to-tickets`.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-2020Z-promote-staging-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to merge staging into main. How will this affect things?

## 2. Facts the AI looked up

- `main` has 5 commits `staging` lacks, all earlier "Merge staging" merges
  (#25, #58, #61, #65, #71). `staging` is 87 commits and 92 files ahead. No
  conflicts; after the merge `main`'s tree equals `staging`'s.
- Production frontend (`les-frontend`) redeploys through `deploy.yml`.
  `frontend/wrangler.jsonc` adds Workers observability at full sampling, with
  logs and traces persisted; staging inherits it, so production gets it too.
- Production backend (Render `les-backend`, `render.yaml`) redeploys once
  Backend CI on `main` is green (`autoDeployTrigger: checksPass`). It gains the
  `scores` module, resolve-only-as-decider, and picks and pools changes.
- No `.sql` changes. One Supabase project serves every environment, so
  production already runs on this schema.
- `e2e.yml` (pull requests only), `frontend-ci.yml` and `close-epic.yml` reach
  `main`.
- Backend CI and Frontend CI on the staging head `0015359` (#127) were
  cancelled after about 6 seconds. With `checksPass`, Render staging likely
  does not run that commit.
- `main` has no branch protection.
- #135 and open PRs #128, #100, #98, #97 and #57 are not on `staging`.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Is this the iter-2 release? | Yes: tag `iter-2` on `main` | No |
| Q2 | Land #135 on staging first? | Yes; other PRs wait | No: it waits its turn in the stack |
| Q3 | Gate: staging CI green, Render staging deployed, staging URLs checked | Yes | Yes |
| Q4 | Promote by a `staging` → `main` PR with a merge commit | Yes, as #25–#71 did | Yes |
| Q5 | Full observability in production | Yes | Yes |
| Q6 | Branch protection on `main` | Yes, separate ticket | Separate ticket |

## 4. Round 2

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q7 | If the re-run CI fails | Fix by a normal PR into `staging`, restart the gate; never fix on `main` | Yes |
| Q8 | `docs/iterations/2/CLAIM.md` reaches `main` untagged | Leave it; tag on a later release promotion | Yes |
| Q9 | Plan complete; no glossary term or ADR | Yes | Yes |

## 5. The plan

1. Re-run the cancelled Backend CI and Frontend CI on the staging head. If
   either fails, fix it through a PR into `staging` and start again.
2. Wait for Render to deploy `les-backend-staging` at that head, then check
   https://les-frontend-staging.les-h.workers.dev by hand.
3. Open a PR from `staging` into `main` and merge it with a merge commit.
4. Confirm the production frontend and backend deploys finish. No tag.

Out of scope: #135 and the other open PRs (they reach `main` in a later
promotion); the `iter-2` tag; branch protection on `main`, which gets its own
ticket.
