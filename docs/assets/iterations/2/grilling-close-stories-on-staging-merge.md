# Grilling session: close stories when their PR merges into staging

- **Date:** 2026-11-19 to 2026-11-20.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below and
  [ADR 0006](../../../adr/0006-stories-close-on-merge-into-staging.md).
  Tickets come next, from `/to-tickets`.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-2049Z-close-stories-on-staging-merge.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I notice that in issue 123, on development panel in GitHub there's no branch
> or pull request associated with the issue, even though pr 128 exists and says
> closes 123 and branch alef/issue-123-e2e-session exist. Why? Can we prevent
> that from happening again?

## 2. Facts the AI found

- #128 targets `staging`; the default branch is `main`. GitHub reads closing
  keywords only on PRs into the default branch, so #128 had no
  `closingIssuesReferences`. The branch was made with git, not from the issue,
  so it was never linked either.
- `docs/agents/issue-tracker.md` already recorded this (added 2026-11-03 in
  `4f0201b`, after iteration 1's AI log noted it) and asked PRs into `staging`
  for `Part of #<n>`. #128's `Closes #123` broke that rule.
- Tests on #123 with throwaway draft PRs (#142, #143, #145) and stack #144, all
  removed afterwards:

| Test | Result |
| :- | :- |
| Branch created with `gh issue develop 123 --base staging` | Shows in Development |
| Plain PR from it into `staging` (#145) | Not linked; the panel kept the branch |
| Stacked linked branch, PR opened by `gh stack link` (#143) | Not linked |
| `addCloseIssueReferences` on #143 (base not `main`) | Linked; `removeCloseIssueReferences` undid it |
| `gh stack link` without `--base` | Moved the bottom PR's base to `main`; the stack then blocked moving it back |

- `addCloseIssueReferences` is in the live GraphQL schema but not in GitHub's
  public reference. No `gh` subcommand wraps it.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Prevent means: (a) the panel shows the work, or (b) also close on merge into `staging` | (a) only | (a), and asked whether (b) is possible without changing the default branch |
| Q2 | Link by creating branches with `gh issue develop`, after a test | Yes | Yes, also test with `gh stack`, and search for a CLI way to link afterwards |
| Q3 | Fix #128 now | Yes | Asked what was wrong with #123's body (the question meant #128's) |

## 4. Round 2

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q4 | Close stories by a workflow when their PR merges into `staging` | Yes | Yes; asked when the `issue-tracker.md` rule was added, since it must change |
| Q5 | A workflow links PRs to issues with `addCloseIssueReferences` | Yes | Yes |
| Q6 | Drop `gh issue develop` | Yes | Yes |
| Q7 | Document `--base staging` for `gh stack link` and `init` | Yes | Yes |
| Q8 | Keep #128's `Closes #123` and link it now | Yes | Yes |

The first try at Q8 was denied by Claude Code's auto-mode classifier. Alef:

> Try again the command, I don't want it to be blocked.

The second try linked #128 to #123.

## 5. Round 3

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q9 | Epics: `close-epic.yml` gets a `workflow_call` trigger, called by the new workflow (`GITHUB_TOKEN` events start no workflows) | Yes | Yes |
| Q10 | A PR merged into a branch other than `staging` closes nothing; close by hand | Yes | Yes |
| Q11 | Stories already in `staging` close through the next promotion PR, one last time | Yes | Yes |
| Q12 | Rewrite `issue-tracker.md` lines 27–33 and the `stacked-prs.md` bullet | Yes | Yes |
| Q13 | ADR 0006, no glossary term (`Done` is a board status) | Yes | Yes |

## 6. The plan

1. A workflow on `pull_request`:
   - `opened`, `edited`, `reopened`, base not `main`: read
     `Closes/Fixes/Resolves #N` from the body (not `Part of`) and link each issue
     with `addCloseIssueReferences`. If the mutation fails, warn and go on.
   - `closed`, merged, base `staging`: close those issues, then call
     `close-epic.yml` for each.
   First check that `GITHUB_TOKEN` may call `addCloseIssueReferences`.
2. `close-epic.yml` gains a `workflow_call` trigger taking the issue number.
3. `docs/agents/issue-tracker.md`: a PR into `staging` says `Closes #<n>`; the
   workflow links it, and the merge closes it and moves it to `Done`; a
   promotion PR lists no issues. `In review` stays a hand move.
4. `docs/agents/stacked-prs.md`: "Issues close when their PR merges into
   `staging`", and `--base staging` on `gh stack link` and `gh stack init`.
5. The next promotion PR carries `Closes #n` for stories already merged into
   `staging`.

Done in the session: #128 linked to #123.
