# Plan to stop worktrees showing as changes

- **Who:** Alef Keuffer.
- **Tools:** Claude Code, Claude Opus 5.5, with the `grill-with-docs` skill.
- **Outcome:** [Grilling record](../../../assets/iterations/3/grilling-untracked-worktrees.md) for ignoring `.claude/worktrees/` and `.idea/` and cleaning up stale worktrees.
- **Delegated:** Diagnosed why the diff view listed many changes (untracked worktree checkouts, not commits), checked each worktree's state, branch and PR, and drafted the decisions.
- **What we decided ourselves, and why:** Alef chose the committed `.gitignore` over a local exclude, so the whole team gets the rule, and kept the evaluation PDF and chat zip out of scope.
- **How we checked:** `git rev-list` against `origin/staging`, `git status` in each worktree, `git branch -r --contains` for each worktree's commit, and `gh pr list` for each branch.
