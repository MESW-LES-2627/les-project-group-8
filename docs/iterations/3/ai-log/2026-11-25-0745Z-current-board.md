# Find the current iteration board automatically

- **Who:** Alef Keuffer.
- **Tools:** Claude Code, Claude Opus 5.5, with the `grill-with-docs` skill.
- **Outcome:** [Grilling record](../../../assets/iterations/3/grilling-current-board.md); `issue-tracker.md` finds the current board and its field ids by name (#193); #191 added to board 26; boards 22 and 24 closed.
- **Delegated:** Diagnosing why #191 was missing from board 26, adding it there, rewriting the doc's snippets, creating #193, closing the old boards and opening the PR.
- **What we decided ourselves, and why:** Alef asked for the board to be found automatically rather than updating the hardcoded ids, and chose to close the old boards now.
- **Where it was wrong:** The first doc edit was made on #191's branch, where another session committed it together with the default-assignee change (`f7aa0cf`); it was redone on its own branch.
- **How we checked:** Ran the new snippet against #191 and #193; it found board 26 and set `Status` and `Estimate`.
