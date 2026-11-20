# Link the stories view from the iteration-2 claim

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review`
  skills from Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** a "Story board" row in [CLAIM.md](../CLAIM.md) linking board
  24's view 1, and the views list in `docs/agents/issue-tracker.md` updated,
  for #160.
- **Delegated:** finding where the claim should link the view; the two doc
  edits; a standards and a spec review in sub-agents; this entry.
- **How we checked:** the live view numbers and filters, read with
  `gh api graphql`; the two reviews. The view filters themselves are set by
  hand in the web UI, since the API cannot edit views.
- **Notes:** the reviews flagged that a recreated view gets a new number and
  breaks the claim link, so the docs now say to edit view 1 in place.
