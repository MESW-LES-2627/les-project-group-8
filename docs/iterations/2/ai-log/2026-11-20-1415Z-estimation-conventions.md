# Document the estimation and classification conventions

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review`
  skills from Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `docs/agents/issue-tracker.md` now states the iteration-3
  estimation, classification and "In progress at start" conventions, for
  #161, stacked on #166.
- **Delegated:** reading the grilling record; the guide edits, including a
  command to set the board's `Estimate` field; a standards and a spec review
  in sub-agents; this entry.
- **How we checked:** the `Estimate` field and project ids, read with
  `gh project field-list`; the two reviews.
- **Where it was wrong:** its first draft said effort "is measured as cycle
  time", which the grilling record contradicts (cycle time is calendar time,
  not effort); it also left the board's auto-add sentence and views list
  under the new estimation paragraph, and the table's later rows still said
  "story". The spec and standards reviews caught all three; fixed in the
  same branch.
- **Notes:** the 1, 2, 3, 5, 8 scale with US22 = 3 was decided for the
  retroactive iteration-2 estimates; carrying it into iteration 3 is the
  AI's reading, not a recorded decision.
