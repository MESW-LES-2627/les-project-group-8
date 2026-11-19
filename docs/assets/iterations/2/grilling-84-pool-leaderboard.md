# Grilling session: US31, see a pool's leaderboard (issue #84)

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below. It fits
  [#84](https://github.com/MESW-LES-2627/les-project-group-8/issues/84) as
  written, so no new tickets.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-1120Z-us31-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to implement 84. I want to use gh stack on top of 117.

## 2. Facts the AI looked up

- US31 is already built on `staging`: US22 (#90) added
  `ScoreService.get_leaderboard`, which orders by most wins, then fewest
  losses, then user id, with competition ranks; `Leaderboard.svelte` shows a
  Rank column.
- `test_us31_leaderboard.py` (commit 761bd2b) already covers AC 31.1–31.5.
- Still missing: US31 is "Next" in the user stories, it has no rows in
  `i02.d004-testing.md`, and the ACs on #84 are unticked.
- [#93](https://github.com/MESW-LES-2627/les-project-group-8/issues/93)
  (needs-triage) proposes ranking by wins only, which changes AC 31.2 and 31.3.
- #84's blocker, #77 (US22), is closed.
- #117 is the top of stack #115: staging ← #113 ← #114 ← #117.
- The frontend has no test runner;
  [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33) plans
  Playwright end-to-end tests.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | #93 before or after #84 | Ship #84 with the current rule; #93 stays a separate follow-up | (a), as recommended |
| Q2 | Scope | Docs and verification only, no production code | Yes |
| Q3 | Manual UI checks | 31.1–31.4 get "plus manual UI check" | See round 2 |
| Q4 | Order of tied Users | Keep user id; note under US31 that the order within a tie isn't meaningful; no glossary change | Yes |
| Q5 | Stack placement | `gh stack add alef/issue-84-pool-leaderboard` on top of #117 | Yes |

On Q3 Alef answered:

> we have a plan to automate checks using playwright later

## 4. Round 2: UI checks

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q6 | UI checks until #33 lands | (a) Check 31.1–31.4 by hand now and list them on #33 | (b): skip the manual check, cite only the backend tests |

> Q6 (b) I think we didn't to the manual cheks for the ones you mentioned. We
> should add them all to 33 and add them as needed to be automated

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q7 | Correct the existing manual-check claims | Rows 16.1–16.2, 24.1 and 27.2 become "UI not yet checked: #33"; list every UI check on #33; leave the 2.11, US5 and pick/detail passages and 25.4 as they are | Yes |

## 5. The plan

- Branch `alef/issue-84-pool-leaderboard`, stacked on #117 in stack #115. PR
  body: "Closes #84. Stacked on #117."
- No production code and no new tests.
- `docs/iterations/2/i02.d003-user-stories.md`: US31 Done in the index and its
  heading, with a note that US22's leaderboard already does this and that the
  order within a tie (by user id) isn't meaningful.
- `docs/iterations/2/i02.d004-testing.md`:
  - rows 31.1–31.5 citing `test_us31_leaderboard.py`; 31.1–31.4 also say
    "UI not yet checked: #33";
  - rows 16.1–16.2, 24.1 and 27.2: "plus manual UI check" becomes
    "UI not yet checked: #33".
- Comment on #33 listing the UI checks to automate: 2.11, US5's header, the
  pick/detail flow, 16.1–16.2, 24.1, 27.2 and 31.1–31.4.
- Tick #84's ACs when the PR merges.
- Out of scope: #93.
- Glossary: no change; Leaderboard and Record already match US31. No ADR.
- Not checked in this session: whether `docs/architecture.md` or the OpenAPI
  file need a US31 mention.

> It covers everything
