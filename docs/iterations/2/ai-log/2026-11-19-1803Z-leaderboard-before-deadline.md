# The Leaderboard above the Bets, and none before the deadline (#135)

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` and `code-review`
  skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** #135 implemented: `GET /api/pools/{id}/leaderboard` returns
  `[]` while the Pool is OPEN, the pool page shows the Leaderboard above the
  Bets and none while OPEN, AC 31.6 in US31, the testing doc, OpenAPI and
  `docs/architecture.md`.
- **Delegated:** writing the AC 31.6 backend test first (red), the
  `ScoreService` rule, moving the Pool's deadline into the past in the shared
  `leaderboard()` step and updating its 12 callers, the page change, the e2e
  case, the docs, and a two-axis review (standards, spec) by sub-agents.
- **What we decided ourselves, and why:** everything in the plan
  ([grilling-leaderboard-before-deadline.md](../../../assets/iterations/2/grilling-leaderboard-before-deadline.md)).
- **How we checked:** backend pytest (156 passed, 2 skipped), `npm run check`
  (0 errors), vitest (36 passed), Playwright e2e on a local Supabase
  (13 passed, including the new 31.6 case). The review found no spec gaps;
  its standards findings on the test helper's name and the test's own Pick
  setup were partly applied (`seed_pick`, architecture doc).
- **Notes:** the page loader still fetches the Leaderboard while the Pool is
  OPEN and discards it; left as is, since the page decides from the Pool's
  status (plan Q11).
