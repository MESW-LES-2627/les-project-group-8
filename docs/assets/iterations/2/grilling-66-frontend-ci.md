# Grilling session: frontend CI (#66)

- **Date:** 2026-11-06, 16:13–16:40.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** [#66](https://github.com/MESW-LES-2627/les-project-group-8/issues/66),
  [#67](https://github.com/MESW-LES-2627/les-project-group-8/issues/67),
  [PR #68](https://github.com/MESW-LES-2627/les-project-group-8/pull/68),
  [PR #69](https://github.com/MESW-LES-2627/les-project-group-8/pull/69).
- **Summary:** see "Frontend CI and planning frontend tests" in the
  [iteration 2 AI log](../../../iterations/2/i02.d005-ai-log.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> Does this project run tests when we push to GitHub ?

The AI read `.github/workflows/` and answered: backend CI runs `pytest` on push
to `main`/`staging`, on pull requests and on manual runs, only when
`backend/**` changes. The frontend has no tests: the deploy workflows only build
it after a merge, and `package.json` has no `test` or `lint` script. It
suggested a `frontend-ci.yml`.

> /mattpocock-skills:grill-with-docs how should we plan this simple frontend-ci.yml ?

## 2. Facts the AI looked up

The skill has the AI look up facts itself and leave only decisions to the user.
Before and between rounds it checked:

- `frontend/package.json` has a `check` script (`svelte-check`), but no test
  runner, ESLint or Prettier.
- `frontend/src/env.ts` makes every env var optional at build time, so CI needs
  no secrets.
- The deploy workflows pin pnpm 12.6.0 and Node 22.
- `main` and `staging` have no branch protection. The only rulesets are the
  course organization's Classroom rules.
- [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33)
  (Playwright end-to-end tests) already exists. Nothing covers Vitest.
- The only project board is "Group 8 — Iteration 1", and the triage labels
  already exist in the repo.

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | What does the job run? | `pnpm check` + `pnpm build` only, no new tooling |
| Q2 | Lint and tests as separate work? | Yes, keep this PR to the workflow file |
| Q3 | When does it run? | Same triggers and path filters as backend CI |
| Q4 | Job shape and toolchain | One job, same pnpm/Node versions as the deploys |

> Q1 (a). Q2 yes, later we'll still think of end to end tests with Playwright and maybe using vitest for frontend unit tests. Q3 yes. Q4 yes.

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q5 | Required check to merge? | Keep it advisory, like backend CI |
| Q6 | Change the deploy workflows? | Leave them alone; they already fail on a broken build |
| Q7 | Cancel superseded runs (`concurrency`)? | Skip it, to match backend CI |
| Q8 | ADR or glossary change? | Neither |
| Q9 | Draft one issue for Playwright + Vitest? | Yes, for review before creating it |

> Q5 keep advisory for now. Q6 yes. Q7 Add it to both CI workflows. Q8 One thing about the glossary the changes in the branch alef/docs-agent-skills weren't approved to merge. Are they here ? I want to at least keep them locally. Q9 I think there is already an issue for Playwright E2E, vitest doesn't have one though.

The AI checked: `alef/docs-agent-skills`
([PR #32](https://github.com/MESW-LES-2627/les-project-group-8/pull/32)) never
touched `GLOSSARY.md`. It adds `AGENTS.md` and `docs/agents/*`, none of which
were in the current checkout, and one of its commits (`4f0201b`) had never been
pushed. #33 exists, so only Vitest needed an issue.

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q10 | Exact `concurrency` setup | Cancel only on pull requests; pushes to `main`/`staging` always finish |
| Q11 | How to keep the agent-skills files | (b) Push `4f0201b`, copy the files into the working tree and list them in `.git/info/exclude` |
| Q12 | Vitest issue text | The drafted text, no labels |
| Q13 | Branch and PR target | `alef/frontend-ci` off `staging`, PR into `staging` |

> Q8 I want to keep these files in all branches I work on. Q10 yes. Q11 (b). Q12 yes. Q13 yes, this work is already for iteration 2.

### Round 4

| Q | Question | AI recommended |
| :- | :- | :- |
| Q14 | A separate issue for the CI work? | Yes, assigned to Alef, on no board until an Iteration 2 board exists |
| Q15 | Vitest issue labels | `needs-triage`, no board, no assignee |

The AI also showed the full plan (commands, issues, branch and files) and said
it would not push or create anything until told to go.

> Q14 yes. Q15 yes. At the end of this session, because I'm logging my ai usage, I want a report of how I used it.

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q7 | Skip `concurrency` | Add it to both CI workflows |
| Q8 | No glossary change | Asked about unmerged changes on `alef/docs-agent-skills`; chose to keep those files on every branch |
| Q9 | One issue for Playwright + Vitest | Playwright already has #33; only Vitest needs one |
| Q13 | Branch off `staging` | Accepted, and placed the work in Iteration 2 |

All other recommendations were accepted as given.

## 5. What the AI did

1. Pushed `4f0201b` to `alef/docs-agent-skills` (PR #32), copied `AGENTS.md`
   and `docs/agents/` into the working tree and listed them in
   `.git/info/exclude`.
2. Created [#66](https://github.com/MESW-LES-2627/les-project-group-8/issues/66)
   "Frontend CI: type-check and build on PRs" and
   [#67](https://github.com/MESW-LES-2627/les-project-group-8/issues/67) "Unit
   tests for the frontend with Vitest".
3. Wrote `.github/workflows/frontend-ci.yml`, added `concurrency` to
   `backend-ci.yml`, and opened
   [PR #68](https://github.com/MESW-LES-2627/les-project-group-8/pull/68) into
   `staging`.
4. Wrote an AI log entry for the session.

Then:

> Set up the iteration 2 docs

5. Created `docs/iterations/2/` following the iteration 1 setup (`765a50a`):
   vision, MVP, user stories, testing, data model and API contract copied with
   `i02` names, a new `CLAIM.md`, an empty iteration backlog and the iteration
   2 AI log. The retrospective is left for the end of the iteration.

> Yes. Can you make an artifact to this session so my ai log usage can reference ?

6. Opened [PR #69](https://github.com/MESW-LES-2627/les-project-group-8/pull/69)
   into `staging` and published a private claude.ai page with this record.

> I want you to save as a markdown.

> I doesn't need the same format word for word. We can use a better one if we can

7. Wrote this file and linked it from the AI log in place of the private page.

## 6. Mistakes and checks

- The AI first proposed no labels on the Vitest issue because the triage-label
  docs weren't merged. It then found the labels already existed and used
  `needs-triage`.
- Its first version of #67's body had a garbled reference to #66. It noticed
  and edited the issue right away.
- After the Q14/Q15 answers, it took them as approval of the whole plan and
  started pushing and creating issues without asking for a separate "go".
- **Checks:** `pnpm install --frozen-lockfile`, `pnpm check` (0 errors, 0
  warnings) and `pnpm build` passed locally. On PR #68, Frontend CI (`verify`,
  39 s) and Backend CI (`test`, 23 s) passed on GitHub. For the iteration 2
  docs, the AI searched for leftover `i01` references and confirmed all 16
  relative links resolve.
