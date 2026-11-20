# Grilling session: US24, see another user's record (issue #82)

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below. It fits
  [#82](https://github.com/MESW-LES-2627/les-project-group-8/issues/82) as
  written, so no new tickets.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-0940Z-us24-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to implement 82

## 2. Facts the AI looked up

- `ScoreService.get_leaderboard` (`backend/scores/service.py`) already returns
  a row for every User with a Pick in the Pool.
- `Leaderboard.svelte` already renders every row and marks the viewer's as
  "(you)"; the pool page already loads it.
- `test_us22_leaderboard.py::test_users_without_picks_in_this_pool_are_absent`
  already covers most of AC 24.3.
- The leaderboard endpoint is public: no auth header.
- US16 hides other Users' outcomes before the deadline, not whether they
  picked.
- [#93](https://github.com/MESW-LES-2627/les-project-group-8/issues/93)
  proposes ranking by wins only, which changes AC 31.2 and 31.3.
- The frontend has no test runner.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Scope | Backend acceptance tests only, no production code; check 24.1 by hand in the browser; mark US24 Done | Yes |
| Q2 | What "friend" means | Any other User; add *friend* to the glossary's _Avoid_ list for User | Yes, with the reason |
| Q3 | Who is viewing | Seed a viewer with their own record next to the other User and assert both rows | Yes |
| Q4 | Showing who picked before the deadline | Acceptable: US16 protects choices, not participation; no ADR | Yes |
| Q5 | Ordering against #93 | Give the two Users different wins so the tests survive #93 | Yes, then revised |

On Q2 Alef asked:

> will you add the reasoning as to why avoid it?

The glossary format keeps _Avoid_ as a bare list, so the reason went into the
User definition: "Users have no friendships or Pool memberships: any other
User is just another User."

## 4. Round 2: Q5 revisited

> Actually for q5 it's good to have a test that would break if we changed
> things, so we probably should have multiple orderings tested

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q6 | Which orderings for AC 24.1 | Four cases: other User above, below, equal wins with fewer losses (breaks under #93), identical record (shared rank 1, ties by user id) | Yes |
| Q7 | Telling #93 | Comment on #93 during `/implement 82` that the US24 test also needs updating | Yes |

Trade-off accepted: the ranking rule is now tested in both the US31 and US24
test files.

## 5. The plan

- Add `backend/tests/acceptance/test_us24_other_users_record.py`. In each
  test a viewer and another User pick in the same Pool and the test asserts
  the full public leaderboard.
  - **24.1:** parametrized over the four orderings in Q6, with exact ranks.
  - **24.2:** the other User's Picks are all on unresolved Bets: a 0–0 row.
  - **24.3:** the other User has Picks only in another Pool: no row.
- No production code changes. Check 24.1 by hand in the browser.
- Mark US24 Done in `docs/iterations/2/i02.d003-user-stories.md` with an
  implementation note.
- Comment on #93 that the new test file needs updating with the rule.
- Glossary: User definition and _Avoid_ list updated in this session. No ADR.

> Confirm. I think everything fits in the current ticket already
