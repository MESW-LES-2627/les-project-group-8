# Staging promoted to production

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` skill from
  Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `staging` at `0015359` merged into `main` by
  [#140](https://github.com/MESW-LES-2627/les-project-group-8/pull/140),
  closing [#138](https://github.com/MESW-LES-2627/les-project-group-8/issues/138).
  No tag.
- **Delegated:** re-running the cancelled Backend CI and Frontend CI on the
  staging head; waiting for Render's staging deploy; probing the staging and
  production sites and backends with `curl`; tracing which issues reach `main`,
  including PRs merged through stacks, to write the `Closes` lines; opening and
  merging #140; watching the production deploys.
- **What we decided ourselves, and why:** Alef checked staging by hand and
  approved the merge before the AI merged it, since the merge deploys to
  production.
- **Where it was wrong:** the first list of issues missed the stacked PRs
  (#114, #117–#121, #127), because they merged into other branches, not
  `staging`. Fixed before the PR opened by checking each PR's merge commit
  against `main..staging`. A wait loop for the Render production deploy keyed
  on the merge commit, but Render reports `0015359`, so it never ended. It
  was stopped by hand.
- **How we checked:** CI green on `0015359` and on `main`; Render deploys
  `success` for `les-backend-staging` and `les-backend`; `/api/health` and
  `/api/pools` respond on both backends; `/`, `/login`, `/signup` return 200 on
  both frontends; `git diff origin/main origin/staging` is empty; no `iter-2`
  tag.
