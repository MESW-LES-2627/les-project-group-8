# A plan to promote staging to main

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** an agreed plan for merging `staging` into `main`. Record:
  [grilling-promote-staging-to-main.md](../../../assets/iterations/2/grilling-promote-staging-to-main.md).
- **Delegated:** comparing the branches; reading the deploy workflows,
  `render.yaml`, `wrangler.jsonc` and the README; checking CI runs, open PRs
  and branch protection with `gh`; asking two rounds of questions with
  recommended answers; writing the record and this entry.
- **What we decided ourselves, and why:** this promotion is not the iter-2
  release, so no tag, though the AI had recommended tagging. #135 waits its
  turn in the stack instead of landing on staging first, as the AI had
  recommended. Branch protection on `main` becomes a separate ticket.
- **How we checked:** git and `gh` output only; nothing was merged or run.
