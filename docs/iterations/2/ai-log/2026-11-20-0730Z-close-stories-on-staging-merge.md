# Stories close when their PR merges into staging

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` and
  `code-review` skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `link-closing-issues.yml` closes the issues a PR closes when it
  merges into `staging` and calls `close-epic.yml` (now `workflow_call`) for
  each; board rules and stacked-PR guide updated, for #149.
- **Delegated:** reading the issue, the plan and ADR 0006; writing both
  workflows and the doc changes; a two-axis review (standards and spec) by
  sub-agents; this entry.
- **Where it was wrong:** the first version let two stories of one epic close
  it twice in parallel; the spec review caught it and `max-parallel: 1` fixed
  it.
- **How we checked:** the body parsing and JSON output were run locally under
  bash; both workflow files parse as YAML. The live acceptance tests (merging a
  test PR into `staging`) were not run yet: the workflow only takes effect once
  it is on `staging`.
- **Notes:** actionlint was not available, and fetching it was blocked.
