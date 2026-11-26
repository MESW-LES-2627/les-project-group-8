# Story gallery of GIFs

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills from Matt Pocock's Skills For Real Engineers.
- **Outcome:** Issue [#218](https://github.com/MESW-LES-2627/les-project-group-8/issues/218): `frontend/e2e/stories.story.ts` has one `USn` test per Done story (25). `.github/workflows/stories.yml` records them on push to `staging` and on a manual run, and publishes `stories/USn.gif` and `stories/README.md` on the `screenshots` branch.
- **Delegated:** Picked the Done stories from the backlog and scripted a demo for each. Moved the Pool, Bet, Pick and Resolution helpers from `screens.showcase.ts` into `e2e/pool.ts`. Wrote the workflow with ffmpeg's palette GIF conversion. Ran two review sub-agents, one for standards and one for the spec, and applied part of their fixes.
- **What we decided ourselves, and why:** Only the page a story opens with `record()` is filmed. Other Users act in contexts of their own, so a GIF shows one person's view without blank stretches. A story that fails is left out of the gallery and fails the run; its recording is not published. The stories share one database, so each story gets its own emails.
- **Where it was wrong:**
  - The first US1 showed a short-password error, but the field's `minlength` stops the form from submitting.
  - US3 and US8 assumed `/` listed only their own Pools.
  - The leaderboard stories ended scrolled away from the Leaderboard.
  - The spec reviewer found four GIFs that didn't show their story's point: US2 had no outcomes, US3 had no closed Pool, US7 ended on the 404 page and US17 had no correct picker. All of these were fixed before the commit.
- **How we checked:** Ran all 25 stories through `run.sh`, converted them to GIFs locally (under 1 MB each) and looked at frames. `pnpm check`, the unit tests (87), the e2e suite (13) and the screens showcase pass. Not checked: the workflow itself, which first runs once this is on `staging`, or on a manual run after it reaches `main`.
- **Notes:** The testing policy (`i03.d004-testing.md`) says e2e tests never share data. The stories do share data and the policy doesn't mention them yet.
