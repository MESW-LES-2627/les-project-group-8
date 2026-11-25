# Mobile viewport in the PR visual diff

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills from Matt Pocock's Skills For Real Engineers.
- **Outcome:** Issue [#219](https://github.com/MESW-LES-2627/les-project-group-8/issues/219): `SHOWCASE=mobile` runs the showcase specs as a `mobile` Playwright project (Pixel 7), writing `showcase/*-mobile.png`. `.github/workflows/screenshots.yml` captures both viewports for the base and the PR, and the comment names changed mobile screens `<screen>-mobile`. GIFs and the e2e suite stay desktop-only.
- **Delegated:** Changed the config and the workflow, checked that a changed mobile screen lands under `test-results/mobile/`, and ran two review sub-agents, one for standards and one for the spec.
- **What we decided ourselves, and why:** Each viewport runs in its own `run.sh` invocation, so each gets an empty database. With both projects in one run they would share a database: the fixed emails would collide, and the pools screen would list both runs' Pools. An env switch picks the project, instead of defining both and passing `--project`, so a plain `SHOWCASE=1` run can't hit that shared-database crash.
- **Where it was wrong:** `npx prettier` reformatted the config with a config that wasn't the project's (double quotes, spaces), so the change was redone by hand.
- **How we checked:** Both viewports pass through `run.sh`. A second mobile run matched the first pixel for pixel. A forced mobile diff came out as `login-mobile-before/after/diff.png` through the workflow's publish loop, run locally. `pnpm check` and the e2e suite (13) pass. Not checked: the workflow on GitHub, which now starts Supabase four times instead of two.
