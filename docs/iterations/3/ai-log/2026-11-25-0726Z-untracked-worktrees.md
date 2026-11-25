# Plan to stop worktrees showing as changes

- **Who:** Alef Keuffer.
- **Tools:** Claude Code, Claude Opus 5.5, with the `grill-with-docs` skill, then `implement`.
- **Outcome:** [Grilling record](../../../assets/iterations/3/grilling-untracked-worktrees.md) for ignoring `.claude/worktrees/` and `.idea/` and cleaning up stale worktrees; then the `.gitignore` change and the local cleanup for [#191](https://github.com/MESW-LES-2627/les-project-group-8/issues/191).
- **Delegated:** Diagnosed why the diff view listed many changes (untracked worktree checkouts, not commits), checked each worktree's state, branch and PR, and drafted the decisions. Then added the ignore rules, removed the 3 linked worktrees, compared the 7 disconnected folders with their last commits before deleting them, unlocked `alef/test-rls-back-door` and ran `git worktree prune`.
- **What we decided ourselves, and why:** Alef chose the committed `.gitignore` over a local exclude, so the whole team gets the rule, and kept the evaluation PDF and chat zip out of scope.
- **How we checked:** `git rev-list` against `origin/staging`, `git status` in each worktree, `git branch -r --contains` for each worktree's commit, and `gh pr list` for each branch. For the cleanup: each disconnected folder was diffed against its commit through a throwaway index, after checking that the diff catches an edit; ignored files were listed too, so local secrets weren't lost.
- **Notes:** `git worktree remove` on `issue-82` failed half-way on Google Drive ("Directory not empty"); its files were clean, so the folder was deleted by hand. Its ignored `supabase/signing_keys.json` (local Supabase keys) was copied aside first.
