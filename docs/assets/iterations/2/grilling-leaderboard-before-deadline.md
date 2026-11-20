# Grilling session: the Leaderboard above the Bets, and none before the deadline

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below. Tickets come next, from `/to-tickets`.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-1700Z-leaderboard-before-deadline-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> Can we add something to pr 118? The leaderboard is under all bet cards,
> which makes the user have to scroll down to check it. It should be easy
> access next to the bets on the right top for example. Will it generate
> conflicts?

## 2. Facts the AI looked up

- PR #118 is docs only (US31 Done) and sits mid-stack:
  #117 ← #118 ← #119 ← #121 ← #127 ← #128 ← #130 ← #131 ← #132.
- No open PR touches `frontend/src/routes/pools/[id]/+page.svelte`; #97 and
  #98 touch `BetCard.svelte` and `ResolveControl.svelte` only. The #132 e2e
  specs find the Leaderboard by its role and name, not its position. So no
  conflicts, but a code commit on #118 would restack #119–#132 and make #118's
  "docs only" description wrong.
- `<main>` is capped at `max-w-3xl` in `+layout.svelte`, too narrow for a side
  column.

## 3. Round 1: where and how

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Where the change goes | New issue and PR stacked on #132; #118 stays docs only | (b), as recommended |
| Q2 | Layout | Side column on wide screens, Leaderboard first on narrow | (b): move the Leaderboard above the Bets everywhere |
| Q3 | Page width for a side column | Widen the pool page only | Not needed after Q2 (b) |
| Q4 | Side column while the Pool is OPEN | Yes, in every status | Replaced by Q5 |

On Q4 Alef asked:

> You mean while all bets inside a pool are open right? Because if a bet has a
> deadline, it should update the leaderboard right?

The AI answered from the glossary: Bets have no deadline of their own; a Pool
has one shared deadline. The Leaderboard changes at each Resolution, which can
only happen after that deadline. The AI also found its Q4 premise was wrong:
while the Pool is OPEN, the Leaderboard lists every User with a Pick at 0–0,
all at rank 1.

## 4. Round 2: before the deadline

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q5 | Leaderboard while the Pool is OPEN | (a) Show it as today | (c): hide it until the deadline has passed |
| Q6 | Placement | After the header and messages, above the Bets heading; "Add a bet" stays at the bottom | Yes |
| Q7 | Tests for the move | None | Yes (reopened as Q10) |

## 5. Round 3: page only, or API too

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q8 | Hide in the page only, or the API too | (a) Page only | (b): the API too |
| Q9 | Record the rule as US31 AC 31.6, in the new PR | Yes | Yes |
| Q10 | Test the new condition | One e2e case for 31.6 | Yes |

Alef asked what the API returns today. The AI found that
`GET /api/pools/{id}/leaderboard` is public and, while the Pool is OPEN,
lists everyone with a Pick, by name and user id, at 0–0. And that every
US22, US24 and US31 acceptance test reads the Leaderboard of a Pool whose
deadline is 7 days ahead, so (b) breaks them unless the tests change.

## 6. Round 4: the API's answer and the tests

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q11 | API response for an OPEN Pool | (a) `200 []`; the page decides from the Pool's status | (a) |
| Q12 | 31.6 covers the API too | Yes: one backend acceptance test plus the e2e case | Yes |
| Q13 | Fix the tests in the shared `leaderboard()` helper | Yes | Yes |

Alef then asked:

> Without it, we won't have the list of participants. Does that break any
> existing user story?

The AI checked every story: none asks to see participants before the
deadline; 15.1 still lists everyone once the deadline has passed; US16 goes
the same way as this change; 22.4 and 24.2 still hold after the deadline.

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q14 | Add "the deadline has passed" to 22.4 and 24.2 | No; 31.6 and the glossary say it | Agreed |

## 7. A check the AI had skipped

The AI had assumed the fake Pool repository could move a deadline. Alef:

> You should check if the pool_repo can do it right? Otherwise why are we
> assuming it can?

`FakePoolRepository` has no such method, but tests already replace a Pool in
`pool_repo.pools` with a new deadline (`test_us29_pool_bets.py`), and
`get_pool` reads that list each time. None of the 13 `leaderboard(client, …)`
calls adds a Bet or Pick afterwards, so moving the deadline at read time is
safe.

## 8. The plan

- A new issue, its PR stacked on #132. #118 stays docs only.
- Pool page: the Leaderboard moves above the Bets heading, after the header
  and messages, and is not shown while the Pool is OPEN.
- `GET /api/pools/{id}/leaderboard` returns `200 []` while the Pool is OPEN.
- US31 gains AC 31.6: given an OPEN Pool with Picks, the API returns an empty
  Leaderboard and the page shows none. One backend acceptance test, one e2e
  case, one row in `i02.d004-testing.md`. 22.4 and 24.2 stay as they are.
- `leaderboard(client, pool_repo, pool)` in `steps.py` moves the Pool's
  deadline (matched by id) into the past before the GET.
- Glossary, Leaderboard: "A Pool has no Leaderboard until its deadline has
  passed."
- No ADR: easy to reverse.
- Seeing who has joined an open Pool is gone; if wanted, it is a new story.
