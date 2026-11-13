# Project evaluation

How to assess this project the way the LES staff score it at each sprint review. Built from two sources:

- The staff's grading sheet (not kept in the repo): the ten lines and their score bands, quoted below.
- [First-class slides](assets/LES-first-class-2026-27-2.pdf): the course rules the sheet assumes (the claim, the caps, living and bound lines).

## What the sheet measures

The sheet is the staff's **dashboard**: ten practice lines, each scored 0–10 per team at each review. It is weather, not the mark. The official mark (0–20) is given in the room at the review, and "a row of tens does not produce 18+". 8–10 means "used and defendable", not rich or numerous.

Lines come in two kinds:

- **Living**: a later review can raise them. Product Vision, User Stories, Acceptance Tests, Unit Tests, Staging/Production server, CI/CD, Repository health.
- **Bound**: final when the review ends. Sprint Retrospective, Product Increment, AI critique.

The sheet has five blocks. Iteration #1 to #4 score all ten lines. Finale scores the nine non-AI lines plus **Product Delivery**, which has no rubric. The sheet does not say which block matches which course review (Iter 0 to Iter 4).

What each review expects:

| Review | Theme | Expected |
| :--- | :--- | :--- |
| Iter 0 | Open | Ready to build: Vision, locked MVP, a thin slice that runs |
| Iter 1 | Move | First increment: the MVP starts to move |
| Iter 2 | Show | Product visible: someone can use it |
| Iter 3 | Harden | Practices show: pipeline, tests, honesty |
| Iter 4 | Ship | Pre-release: last increment plus current practice health |

## Rules that cap scores

- **The claim is the entry point.** The staff open tag `iter-N` and `docs/iterations/N/CLAIM.md` on that tag, then follow only its permalinks: this tag, compare with the last tag, production, staging, pipeline, MVP, Vision, stories in this increment, how to run the tests, retrospective, AI log, and team artefacts someone will be asked to open. They do not browse the repository.
- **A dead link caps its line at 4.**
- **A missing tag or claim** caps the team mark for that iteration at 10/20, and scores Repository health 0.
- The claim carries no self-score. A wiki page that is not on the tag counts for nothing. A Friday dump is not history.

The house **Definition of Done**. Teams may add lines but not delete these five:

1. It runs on the tag, not only on one laptop.
2. It matches an MVP outcome (a user-visible thing the product must do), or an explicit public cut.
3. A check exists that would fail if the change broke. Iter 0: a walkthrough is enough. From Iter 1, automation must appear and grow.
4. The change is in history on the tag, not a Friday dump.
5. Any of you could open it. If only the author can, it is not team-done.

## How to assess

1. Fix the iteration `N`. Ask if it was not given. If tag `iter-N` does not exist yet, assess the current branch as a pre-review check and say so in the report.
2. Read the claim on the tag (`git show iter-N:docs/iterations/N/CLAIM.md`) and open every permalink. Record each dead link and each permalink the rules above require that the claim lacks.
3. Score every line of the block against its bands below. Evidence counts only when it is reachable from the claim. Evidence you find elsewhere goes in the report as "exists but unlinked" and does not raise the score.
4. Report.

You are done when every line has a score, the quoted band it lands in, the link you opened as evidence, and the smallest change that would reach the next band.

Report format:

| Line | Score | Band (quoted) | Evidence | Next band needs |
| :--- | :--- | :--- | :--- | :--- |

Close the report with the claim's dead and missing links, and the caps they trigger.

## The ten lines

Bands are quoted verbatim from the sheet. "Look for" turns each band into checks against this repo. Use `gh` for issues, the board, pull requests and branch protection.

### 1. Product Vision (living)

- 0: No Vision linked.
- 1–4: Generic pitch. Purpose or actors missing. Reads like an unedited generated brochure.
- 5–7: Goal, stakeholders and horizon are named. Fit with the MVP is visible.
- 8–10: Concise; non-goals explicit; all the product vision board items are filled, clear and defendable.

Look for: the Product Vision Board fields (vision, target group, needs, product, business goals), each filled in. Explicit non-goals ("what is out" in the MVP). An MVP of three to five outcomes, each something a user can do; more than six is "the Vision leaking". The MVP was locked at the end of Iter 0. It may be cut or expanded in public, never quietly replaced.

### 2. User Stories (living)

- 0: No stories linked.
- 1–4: A list, or a generated dump. Not buildable. Not tied to an MVP outcome.
- 5–7: Clear and tied to outcomes. Missing assignee, estimate, or acceptance-test link.
- 8–10: Ready. Assigned. Estimated. Traced to acceptance tests. INVEST. Split where a story is not.

Look for: open "stories in this increment", then each GitHub issue it names. Each story has an assignee, an estimate, a link to its acceptance tests, and an MVP outcome. Oversized stories are split.

### 3. Acceptance Tests (living)

- 0: None linked.
- 1–4: Textual, unused, or not about an MVP outcome.
- 5–7: Clear textual checks. A person could follow them. Not automated.
- 8: Automated. A broken path fails a check. Not yet in the pipeline.
- 9–10: Automated, tied to the outcome, and run in the pipeline.

Look for: each story's acceptance criteria mapped to an automated test, and a CI job on the tag that runs those tests.

### 4. Unit Tests (living)

- 0: No tests, or nothing present.
- 1–4: Tests exist. No metrics report. No testing policy. Or a report on getters and generated noise.
- 5–7: A metrics report is linked. The testing policy says what is tested and what is not. Metrics are thin, or the policy is a slogan.
- 8: Metrics report and testing policy agree. The metrics are about logic that can break, not only coverage of the repo.
- 9–10: The above, and the metrics report shows the tests arriving with the changes. Not a final campaign.

Look for: a testing policy that names what is not tested and why. A linked metrics report. Tests that cover domain logic. In the compare `iter-(N-1)...iter-N`, tests land in the same pull requests as the code they cover.

### 5. Sprint Retrospective (bound)

- 0: None linked.
- 1–4: Missing a heading, a generated list, or only team mood.
- 5–7: All three headings. Specific. Process is present; product may be.
- 8–10: Process is the body. Product is secondary. One item from the previous Do differently is visible in this tag. Next action named.

Look for: three headings. The sheet names only "Do differently". Items about process, specific enough to act on. The previous retrospective's "Do differently" item, visible as a change in the compare. A named next action.

### 6. Product Increment (bound)

- 0: Nothing to run.
- 1–4: A final commit exists; no clear release; or the demo does not match the tag.
- 5–7: Tagged release, related to the plan, runs.
- 8–10: Value against the MVP is obvious on the machine; debt named; not a different product.

Look for: the tag runs, and its content matches the iteration backlog. Each delivered story maps to an MVP outcome. Known debt is written down. The review ends in one of "accept", "accept with debt" or "a different product".

### 7. Staging/Production server (living)

- 0: No servers.
- 1–4: Something is up; not used as the delivery path.
- 5–7: One environment used honestly and is reachable.
- 8–10: Both exist, match the named branches, review done on production or a tagged promote, not only on a laptop.

Look for: both URLs in the claim respond. The deploy workflows map each environment to a named branch. Production gets the tag through the pipeline, not a manual script.

### 8. CI/CD (living)

- 0: No pipeline.
- 5: A pipeline exists.
- 6–8: Tests and deploy run.
- 9–10: Extra checks and a red build is treated as a stop. A green pipeline that does not run their tests is a 5.

Look for: workflows that run the project's own tests and deploy. Extra checks such as lint, types or coverage. Required status checks or branch protection, so a red build blocks the merge.

### 9. Repository health (GitHub) (living)

- 0: No usable repo, or no CLAIM.md on the tag.
- 1–4: No board, or a stale or generated board. No pull request, or one dump. Issues unassigned. Increment not findable.
- 5–7: Board in use. Stories are issues. Some assignees, a few labels, one real pull request. Claim links work.
- 8–10: Done is what ran. Assignees match the week. Pull requests brought the increment in. Not a Friday dump.

Look for: a current board. Closed issues match what runs on the tag. Assignees match who did the work. The increment arrived through reviewed pull requests, with commits spread across the iteration.

### 10. AI critique (bound)

- 0: No log.
- 1–4: Tools only, or an account with no change linked. "We used Copilot."
- 5–7: Account of this iteration. A linked change. The decision not delegated is thin.
- 8–10: Account shows assistance, not replacement. A key decision is human. One concrete miss, and the change is linked.

Look for: one group disclosure for this iteration that names the tools. A key decision the team made itself, and why. One concrete place the model was wrong, with a link to the change that fixed it.

### Product Delivery (Finale only)

The sheet has no rubric for this line. Score it against the Iter 4 expectation (the last increment plus current practice health) and mark the score as unanchored.
