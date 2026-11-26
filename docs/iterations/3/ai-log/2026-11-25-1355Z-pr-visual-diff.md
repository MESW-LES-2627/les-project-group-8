# PR visual diff for the login screen

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills from Matt Pocock's Skills For Real Engineers.
- **Outcome:** Issue [#216](https://github.com/MESW-LES-2627/les-project-group-8/issues/216): a login showcase spec and `.github/workflows/screenshots.yml`, which posts a before/after/diff PR comment from an orphan `screenshots` branch.
- **Delegated:** Wrote the showcase spec, the `SHOWCASE` switch in the Playwright config, the workflow and the README section. Ran two review sub-agents, one for standards and one for the spec, and applied their fixes.
- **Where it was wrong:** The first version of the push-retry loop had no git identity for the rebase and no cap on retries. Under a push race it would have spun until the job timed out. The spec reviewer caught it and it was fixed before the PR.
- **How we checked:** Ran the showcase locally through `run.sh`, once with a changed login heading to get a real mismatch report. Tested the crash filter on that report and on a forged crash. Dry-ran the Publish step with stubbed `git` and `gh` for all three comment variants. `pnpm check`, unit tests (87) and the e2e suite (13, showcase excluded) pass. The workflow itself has not run yet; that needs a pushed PR.
