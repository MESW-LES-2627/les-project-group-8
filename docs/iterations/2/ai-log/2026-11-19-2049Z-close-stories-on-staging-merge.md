# A plan to close stories when their PR merges into staging

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** an agreed plan and
  [ADR 0006](../../../adr/0006-stories-close-on-merge-into-staging.md) for
  linking and closing stories from PRs into `staging`. Record:
  [grilling-close-stories-on-staging-merge.md](../../../assets/iterations/2/grilling-close-stories-on-staging-merge.md).
- **Delegated:** finding why #128 did not show on #123 (base `staging`, not the
  default branch); reading GitHub's docs and the GraphQL schema, which turned up
  the undocumented `addCloseIssueReferences`; testing linked branches, `gh stack`
  and the mutation with throwaway PRs #142, #143 and #145, then removing them;
  linking #128 to #123; three rounds of questions; writing the ADR, the record
  and this entry.
- **What we decided ourselves, and why:** close stories on merge into
  `staging`, which the AI had first advised against, to drop the hand-typed
  `Closes` list from promotions. Test with `gh stack` too, which showed that
  `gh stack link` without `--base` retargets the bottom PR to `main`.
- **Where it was wrong:** it first said the panel would need a hand link in the
  UI because no API existed; Alef's request to search found the mutation. Its
  Q3 said "fix #123" when it meant #128's body.
- **How we checked:** GraphQL queries of #123's linked branches and PRs after
  each test, and again after cleanup.
