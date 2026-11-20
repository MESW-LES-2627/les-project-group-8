# A plan to move the Leaderboard above the Bets and hide it before the deadline

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** an agreed plan for a new issue stacked on #132, and a glossary
  rule. Record:
  [grilling-leaderboard-before-deadline.md](../../../assets/iterations/2/grilling-leaderboard-before-deadline.md).
- **Delegated:** checking open PRs for conflicts with #118; reading the pool
  page, layout, leaderboard endpoint, user stories, glossary and acceptance
  tests; asking four rounds of questions with recommended answers; editing the
  glossary; writing the record and this entry.
- **What we decided ourselves, and why:** keep #118 docs only and put the
  change in a new PR. Move the Leaderboard above the Bets instead of the AI's
  side column. Hide the Leaderboard, in the page and in the API, until the
  Pool deadline has passed; the AI had recommended keeping it (page and API)
  as it is.
- **Where it was wrong:** it first said the Leaderboard was empty while the
  Pool is OPEN; the code lists every User with a Pick at 0–0, corrected in the
  next round. It assumed the fake Pool repository could move a deadline
  without checking; Alef asked it to check, and it found the existing pattern
  (record, section 7).
- **How we checked:** read the code paths the plan relies on; nothing was run.
