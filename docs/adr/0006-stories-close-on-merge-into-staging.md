# Stories close when their PR merges into staging

Our feature PRs target `staging`, but GitHub reads `Closes #N` only on PRs into
the default branch, `main`. So a story's PR never showed in the issue's
Development panel, and stories were closed by hand-typed `Closes` lines in the
promotion PR. We now close a story when its PR merges into `staging`: a workflow
links each PR to the issues its body closes (`Closes/Fixes/Resolves #N`) through
the GraphQL mutation `addCloseIssueReferences`, and closes them when the PR
merges into `staging`. A story in `Done` therefore means merged into `staging`,
not live on `main`.

## Considered options

- **Make `staging` the default branch:** GitHub would link and close on its own,
  but the repo's home branch would no longer be the released code.
- **Create branches from the issue (`gh issue develop`):** the branch shows in
  the panel, but a PR opened from it into `staging`, plain or through
  `gh stack link`, did not replace it there (tested on #123), and it does not
  fit `gh stack add`, which creates the branch itself.
- **Link by hand in the issue sidebar:** works, but cannot be scripted and gets
  forgotten.

## Consequences

- `addCloseIssueReferences` is missing from GitHub's public GraphQL reference.
  If it changes or disappears, the panel stays empty, but the merge still closes
  the issue from the PR body.
- Issues closed with `GITHUB_TOKEN` do not start other workflows, so
  `close-epic.yml` is called from the new workflow (`workflow_call`) instead of
  relying on its `issues: closed` trigger.
- A PR merged into a branch other than `staging` (a stack member not retargeted
  first) closes nothing; its issue is closed by hand.
- Stories merged into `staging` before this change are closed by the next
  promotion PR, with one `Closes #n` each, one last time.
