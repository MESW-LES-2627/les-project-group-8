# Issue tracker: GitHub

Epics and user stories for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --json number,title,body,labels,comments`.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Make an issue a sub-issue of a parent**: `gh issue create --parent <parent> ...`, or `gh issue edit <parent> --add-sub-issue <child>` afterwards (`gh` 2.94+). Older `gh`: `gh api --method POST repos/<owner>/<repo>/issues/<parent>/sub_issues -F sub_issue_id=<child-db-id>` (database id, as in **Blocking** below). Without sub-issues, put `Part of #<parent>` at the top of the child body.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Project board

Issues are tracked on the current iteration's org project, **Group 8 — Iteration N** (owner `MESW-LES-2627`): the open project with that title and the highest number. Never hardcode its number or ids; the snippets below look them up. Work is two levels deep: an **epic** (label `epic`) is a parent issue whose sub-issues are **user stories** (label `user-story`). Technical work has issue type `Task` and defects issue type `Bug`; both go on the board too, with no story. Stories keep the `user-story` label; never write technical work as an "As a developer…" story. The board's `Status` field has `To do`, `In progress`, `In review`, `Done`. Sub-issues of an issue already on the board are added to it automatically, in `To do`, so epics stay in the project. Its views:

- **Iteration N board**: stories only (`label:user-story`), in swimlanes by `Parent issue`. Each iteration's claim links it as `views/1`, so edit it in place and never recreate it.
- **Technical work**: Tasks and Bugs (`type:Task,Bug`).
- **Epics**: a table of epics with their `Sub-issues progress`.
- **Roadmap**: epics only.

Earlier iterations' boards are closed and kept as a record; never add issues to them.

From iteration 3, every story, Task and Bug gets points in the board's `Estimate` field at iteration planning, before work starts (Fibonacci 1, 2, 3, 5, 8, with reference story US22 #77 = 3; split anything over 8). Report story points and task points (Tasks and Bugs) separately. Cycle time is read from the `Status` history; hours are not logged.

GitHub's board automation only reacts to issues **linked** to a PR, and `Closes #N` only links when the PR targets `main`. Our feature PRs target `staging`, so `.github/workflows/link-closing-issues.yml` links each PR to the issues its body closes (`Closes`, `Fixes`, `Resolves #<n>`), and closes them once its commits are in `staging`, stack members included (ADR 0006). `Done` means merged into `staging`, not live on `main`. This needs the `project` scope on `gh` (`gh auth refresh -h github.com -s project`) for the hand moves below. Epics are never moved by hand.

| When | Do |
| :--- | :--- |
| A new iteration starts | Create its board, switch on its **Auto-add to project** workflow (Project → Workflows, filtered to this repo; UI only), and close the previous board. |
| Iteration planning (from iteration 3) | Set `Estimate` on every story, Task and Bug planned for the iteration. |
| You start an issue (story, Task or Bug) | Assign it (`gh issue edit <n> --add-assignee @me`) and set it `In progress` before the first commit, so its cycle time is right. |
| Its PR into `staging` opens | Set the issue `In review` by hand. List it in the PR body as `Closes #<n>` (one keyword per issue); the workflow links it. |
| The PR merges into `staging` | The workflow closes the issue; `Item closed` moves it to `Done`. Once an epic's last story closes, `.github/workflows/close-epic.yml` closes the epic, whether the story was closed by the workflow or by hand. |
| `staging` is promoted to `main` | The promotion PR lists no issues (except once, below). |

A stack member merged into its parent branch closes its stories when that branch's commits reach `staging`. A PR whose commits never reach `staging` closes nothing.

One time only: stories merged into `staging` before ADR 0006 are closed by the next promotion PR, with one `Closes #<n>` each.

**Find the board and the issue's item** (adding an issue that is already on the board returns its existing item):

```sh
o=MESW-LES-2627
proj=$(gh project list --owner $o --format json \
  --jq '[.projects[] | select(.closed | not) | select(.title | startswith("Group 8 — Iteration"))] | max_by(.number) | .number')
pid=$(gh project view "$proj" --owner $o --format json --jq .id)
item=$(gh project item-add "$proj" --owner $o --url "https://github.com/$o/les-project-group-8/issues/<n>" --format json --jq .id)
```

**Set a status** (`To do`, `In progress`, `In review` or `Done`):

```sh
field=$(gh project field-list "$proj" --owner $o --format json --jq '.fields[] | select(.name=="Status") | .id')
opt=$(gh project field-list "$proj" --owner $o --format json --jq '.fields[] | select(.name=="Status") | .options[] | select(.name=="<status>") | .id')
gh project item-edit --id "$item" --project-id "$pid" --field-id "$field" --single-select-option-id "$opt"
```

**Set an estimate**:

```sh
field=$(gh project field-list "$proj" --owner $o --format json --jq '.fields[] | select(.name=="Estimate") | .id')
gh project item-edit --id "$item" --project-id "$pid" --field-id "$field" --number <points>
```

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh api --paginate 'repos/{owner}/{repo}/pulls?state=open' --jq '.[] | select(.author_association | IN("OWNER","MEMBER","COLLABORATOR") | not) | {number, title, author: .user.login, author_association, labels: [.labels[].name]}'`.
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Read it as in **Read an issue** above.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (see **Make an issue a sub-issue of a parent**). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions-so-far.
