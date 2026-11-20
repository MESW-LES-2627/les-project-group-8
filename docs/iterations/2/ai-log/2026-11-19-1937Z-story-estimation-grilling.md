# Decided how to estimate iteration 2's stories after the fact

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** twelve decisions on retroactive story points, classifying
  technical work and board views, recorded in
  [grilling-story-estimation.md](../../../assets/iterations/2/grilling-story-estimation.md).
- **Delegated:** reading `docs/evaluation.md` and the iteration docs; pulling
  board 24's status history, PR sizes, reviews and commit times with `gh`;
  proposing each decision with a recommendation; this entry and the record.
- **What we decided ourselves, and why:** no blind planning poker; size the
  closed stories from what they actually took (board history, PRs, reviews),
  because that data exists and the forecast is already lost. Keep technical
  work off the stories view so the board stays readable.
- **Where it was wrong:** it treated US24 and US31 as open from a stale
  snapshot (Alef caught it), and only looked at board history once Alef asked
  whether more data existed.
- **How we checked:** every number in the record's table comes from `gh`
  queries run in the session.
