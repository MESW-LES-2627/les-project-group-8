# Docs link check in CI, and a links rule for AI log entries

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` skill from Matt
  Pocock's Skills For Real Engineers, lychee 0.24.2.
- **Outcome:** implemented
  [#187](https://github.com/MESW-LES-2627/les-project-group-8/issues/187): a
  `docs-links.yml` workflow, the Links rule in
  [`ai-log.md`](../../../ai-log.md), and the three existing dead links fixed.
- **Delegated:** wrote the workflow and the rule from the plan in
  [grilling-docs-link-check.md](../../../assets/iterations/3/grilling-docs-link-check.md),
  fixed the dead links, and ran the checks below.
- **How we checked:** lychee with the workflow's arguments on the whole tree
  (0 errors), then with a planted dead anchor in a relative link and in an
  `iter-3` permalink (both reported, plant removed). The remap with
  `${{ github.workspace }}` is first exercised by the PR's own CI run.
