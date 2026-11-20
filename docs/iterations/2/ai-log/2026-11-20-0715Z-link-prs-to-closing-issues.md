# A workflow that links PRs into staging to the issues they close

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` and
  `code-review` skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `.github/workflows/link-closing-issues.yml`, for #147, in PR #151.
- **Delegated:** reading the issue, the plan and ADR 0006; introspecting the
  `addCloseIssueReferences` input; writing the workflow; opening draft PR #151
  into `staging` to test it; a two-axis review by sub-agents; this entry.
- **How we checked:** on PR #151, the run with `GITHUB_TOKEN` linked #147 from
  `Closes #147` and left `Part of #149` unlinked; adding `Closes #999999` to the
  body ran it on `edited`, which warned and still passed. The issue-number
  parser was run on sample bodies with GNU grep. `actionlint` reported only
  info-level notes.
- **Notes:** the link from #151 to #147 is the real one and was kept, so there
  was nothing to remove with `removeCloseIssueReferences`.
