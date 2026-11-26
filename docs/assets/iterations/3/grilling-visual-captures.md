# Grilling session: screenshots and GIFs of the app

- **Date:** 2026-11-25.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below, to be split into tickets with `/to-tickets`. No
  glossary terms (this is tooling, not product language) and no ADR (every
  choice is undone by deleting a workflow or a branch).
- **Summary:** see the
  [raw AI-log entry](../../../iterations/3/ai-log/2026-11-25-1330Z-visual-captures-plan.md).

Alef's messages are quoted word for word. The AI's questions are shortened to
their decision and its recommended answer.

## 1. How it started

> Can we have it so that we automatically generate pictures and gifs of our
> application? For example, one per user story? And/or something that makes it
> so when we have a PR that changes the frontend we automatically get
> screenshots/gifs with before/after depending on what code was touched?

## 2. Facts the AI looked up

- Playwright e2e specs live in `frontend/e2e/`. `e2e.yml` runs them on PRs
  against a throwaway local Supabase ([ADR 0005](../../../adr/0005-e2e-tests-use-a-throwaway-local-supabase.md)),
  with no secrets.
- Test titles already name the story or AC they cover, e.g. `(US5)`,
  `(31.1–31.3)`. Their data is random (`Pool ${uuid}`), so screenshots of them
  would differ on every run.
- Nothing captures screenshots or video today; traces are kept only on failure.
- PR [#212](https://github.com/MESW-LES-2627/les-project-group-8/pull/212)
  (Vitest browser mode) already installs Chromium in Frontend CI.

## 3. Decisions

| # | Question | Decision |
| - | - | - |
| Q1 | Which first: story gallery or PR visual diff? | Both, on one capture layer. The PR visual diff ships first. Alef: "remember we have to build stacked on top of pr 212." |
| Q2 | Reuse e2e specs or write new ones? | Separate showcase specs in `frontend/e2e/`, run through `run.sh`, with fixed data and a frozen clock (`page.clock`). |
| Q3 | Which screens a PR shows | Capture every screen on every frontend PR; show only the ones whose pixels changed. No mapping from files to routes. |
| Q4 | Where "before" comes from | Build the PR's base in the same job (second worktree) and run the head's showcase specs against it. If that fails, the comment shows the head's screens only. |
| Q5 | Where images live | An orphan `screenshots` branch, linked from a single PR comment that the workflow edits on each push. |
| Q6 | PNG or GIF | PNG pairs for PR diffs; one GIF per story (ffmpeg from Playwright's webm). |
| Q7 | How showcase data is created | Through the UI with the `account.ts` helpers and fixed names. |
| Q8 | How images are compared | Playwright's `toHaveScreenshot`: `--update-snapshots` on the base writes the expected images, and the head run fails on the screens that changed. No new dependency. |
| Q9 | Trigger and blocking | New `screenshots.yml` on `pull_request`, `paths: frontend/**`. Not a required check; red only if the head's specs crash. |
| Q10 | Story gallery | One showcase test per story that has a UI, titled `USn …` (no test for Obsolete or Later stories). On push to `staging`, record each one, convert it to `stories/USn.gif` on the `screenshots` branch and rewrite `stories/README.md` there. |
| Q11 | Viewports | Desktop Chrome only. Alef: "create a issue later" for a mobile viewport. |
| Q12 | Growth of the `screenshots` branch | `pr/<n>/` is overwritten on each push and never pruned, marked with a `shortcut:` comment. Links point to commit SHAs, so old comments keep working. |
| Q13 | PR comment contents | One comment, edited on each push: a before / after / diff row for each screen that changed, or "No visual changes", or "After only (base could not be captured)", plus a link to the run. |

## 4. Tickets to create

1. **Showcase specs:** fixed data, frozen clock, one `toHaveScreenshot` per
   screen and one `USn` test per story with a UI. Stacked on #212.
2. **PR visual diff workflow:** `screenshots.yml`, the base/head runs, the
   `screenshots` branch and the PR comment (Q3–Q5, Q8, Q9, Q12, Q13).
3. **Story gallery:** GIFs and README on push to `staging` (Q6, Q10).
4. **Follow-up:** a mobile viewport as a second Playwright project (Q11).

## 5. Addendum: review of PR #224 (2026-11-26)

Joaolfc0's [review comment](https://github.com/MESW-LES-2627/les-project-group-8/pull/224#issuecomment-7194917707)
raised two points: the gallery adds about 10 MB to the `screenshots` branch on
every push to `staging`, which is never pruned, and the 387 lines of story
tests must be kept in step with every UI change. Alef's answer, with Claude
Code running the `grilling` skill:
[reply on the PR](https://github.com/MESW-LES-2627/les-project-group-8/pull/224).

Facts the AI looked up: `staging` got 45 first-parent pushes in the month to
2026-11-26, so about 450 MB of GIF history a month. GIFs don't delta-compress
and recordings are never byte-identical. A plain `git clone` fetches every
branch, so the growth reaches every clone. `stories.yml` is not a required
check and runs only after a merge to `staging`.

| # | Question | Decision |
| - | - | - |
| Q14 | How to stop the gallery's history growing | Publish it to its own `stories` branch, replaced on each run by a single orphan commit with a force-push. Don't force-push `screenshots`: PR comments link to its commit SHAs (Q12). Not a workflow artifact: it expires and can't be viewed in the browser. The push retry loop goes, since the workflow's `concurrency` group already serializes story runs. |
| Q15 | Is the gallery worth its upkeep | Keep all 25 stories. A broken story never blocks a merge; it drops its GIF and turns the staging run red. A UI change already means editing that flow's e2e tests. |
| Q16 | `pr/<n>/` growth on `screenshots` | Unchanged (Q12): small PNGs of changed screens only. Said so in the reply. |

The fix lands on PR #224 itself, in a fresh `/implement 218` session that also
updates the PR title and body to name the `stories` branch.
