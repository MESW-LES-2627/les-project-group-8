# Stacked PRs close their issues once their commits reach staging

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review`
  skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `link-closing-issues.yml` now closes the issues of every merged
  PR whose merge commit is in `staging`, walking down the stack from each
  merged PR; ADR 0006 and the board and stacked-PR guides updated, for #155.
- **Delegated:** reading the issue, workflow and docs; probing GitHub's API on
  the real stack (#128 to #136); writing the workflow and doc changes; a
  two-axis review by sub-agents; this entry.
- **What we decided ourselves, and why:** option 2 of #155 (a workflow, not
  retargeting stack PRs by hand).
- **Where it was wrong:** the first idea, matching commits to PRs with
  `commits/{sha}/pulls`, returns only the bottom PR, and the second, walking
  only PRs merged before the bottom PR, missed them all: a whole-stack merge
  marks members merged a second after the bottom PR. Both were caught by
  dry runs against #128 before committing. The reviews then caught a stray
  `queue` file committed from a dry run, a walk with no visited set that could
  loop through `staging` back-merges, and API failures that skipped issues
  silently; all fixed before the PR.
- **How we checked:** the step's script was run locally against the real
  stack, with `gh issue close` replaced by `echo`: from #128 it closes #123,
  #124, #129, #125 and #135 (the issues closed by hand on 2026-11-20); from
  #132 only #125 and #135; a commit outside `staging` reads `diverged` and a
  bad SHA warns. The live workflow was not run: it takes effect once on
  `staging`.
- **Notes:** works only with merge commits; a squashed or rebased stack branch
  needs its members' issues closed by hand (ADR 0006). actionlint and
  shellcheck were not installed.
