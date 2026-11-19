# Stacked PRs

We chain dependent PRs with the `gh stack` extension (`github/gh-stack`). The trunk is `staging`.

- **Start work on a stack:** check out its top branch, then `gh stack add <branch>` before the first commit. The new branch sits on the stack from the start.
- **Put an existing branch or PR on a stack:** `gh stack link <bottom> … <top>`, every member in order, as branch names, PR numbers or URLs. It keeps the PRs already in the stack and opens PRs for branches that lack one. `.git/gh-stack` is `gh stack`'s own state: change it only through `gh stack`.
- **Push and open PRs:** `gh stack submit --auto`, then set each new PR's title and body with `gh pr edit`.
- **"Stack N"** is a stack number, separate from PR and issue numbers: `gh api repos/MESW-LES-2627/les-project-group-8/stacks/N` lists its PRs in order.
- **Issues stay open on merge**, because the PRs target `staging`: see the project board rules in `issue-tracker.md`.

On a Mac, Finder can drop a `.DS_Store` into `.git/worktrees`, and every local `gh stack` command then fails with `worktree administration path ".../.DS_Store" is not a directory`. Delete that file and rerun.
