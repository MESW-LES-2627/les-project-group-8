# E2E specs for the Leaderboard after the deadline, 24.1 and 31.1–31.4

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills
  from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills),
  Playwright 1.65.1.
- **Outcome:** `frontend/e2e/leaderboard.spec.ts` for
  [#125](https://github.com/MESW-LES-2627/les-project-group-8/issues/125); the
  24.1 and 31.1–31.4 rows in `i02.d004-testing.md` point at it.
- **Delegated:** writing the two specs. Setup writes Users (through Supabase
  Auth's admin API), a Pool whose deadline has passed, Bets, Picks and winning
  Outcomes straight to the local database with its secret key, then a User logs
  in and reads the Leaderboard. One Pool gives ranks 1, 2, 2, 4 and covers 24.1
  and 31.1–31.3; a second Pool with no Picks covers 31.4. The review ran as two
  sub-agents (standards, spec).
- **Where it was wrong:** the first draft copied `signUp`'s email and name
  scheme. The standards reviewer flagged it, and both now use `newAccount()`
  in `account.ts`. It also named a seeded Bet's handle `Bet`, which is now
  `SeededBet`, and said "winners" where the glossary says "winning Outcomes".
- **How we checked:** `pnpm test:e2e` passes (12 tests); `pnpm check` passes.
- **Notes:** the spec reviewer noted that `ScoreService` never reads the
  deadline, so these tests would pass with a future deadline too. The browser
  only shows the Leaderboard; the deadline is set because the plan asked for
  it. `e2e` has no `@types/node`, so the spec declares `process` itself.
