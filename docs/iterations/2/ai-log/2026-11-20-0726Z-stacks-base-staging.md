# The stacked-PR guide keeps `gh stack` stacks on staging

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` skill
  from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `--base staging` for `gh stack init` and `gh stack link` in
  `docs/agents/stacked-prs.md`, for #148.
- **Delegated:** reading the issue and Q7 of the plan; checking both commands'
  `--help` for the `--base` flag; editing the guide; this entry.
- **How we checked:** `gh stack init --help` and `gh stack link --help` both
  list `--base` and default to the repository's default branch.
