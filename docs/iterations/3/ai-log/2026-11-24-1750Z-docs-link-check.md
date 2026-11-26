# Plan to stop dead links in the docs

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`), lychee 0.24.2.
- **Outcome:** a plan for a links rule in [`ai-log.md`](../../../ai-log.md)
  and a lychee CI job, recorded in
  [grilling-docs-link-check.md](../../../assets/iterations/3/grilling-docs-link-check.md).
- **Delegated:** ran lychee on `origin/staging` and on the PR #174 branch,
  found the one existing dead link, tested `--remap` for `CLAIM.md` tag
  permalinks, asked the questions and wrote the record.
- **What we decided ourselves, and why:** Alef asked how `CLAIM.md` links to a
  tag that doesn't exist yet get checked; the AI's earlier answer had left them
  to a hand check. That led to remapping them to the local tree in CI.
- **Where it was wrong:** the first lychee run used only `docs/`, so 30 links
  into code showed as false errors; caught and re-run on the full tree in the
  same session.
- **How we checked:** lychee runs on `origin/staging` (1 dead link) and
  `origin/iteration-3-planning` (the 2 PR #174 anchors caught), plus a planted
  bad remapped anchor.
