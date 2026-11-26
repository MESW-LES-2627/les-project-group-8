# Grilling session: triage of issues #33 and #120

- **Date:** 2026-11-25.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33)
  closed as done; [#120](https://github.com/MESW-LES-2627/les-project-group-8/issues/120)
  specified, estimated and moved into iteration 3 under
  [#186](https://github.com/MESW-LES-2627/les-project-group-8/issues/186).
- **Summary:** see the
  [raw AI-log entry](../../../iterations/3/ai-log/2026-11-25-1321Z-triage-33-120.md).

Alef's messages are quoted word for word. The AI's questions are shortened to
their decision and its recommended answer.

## 1. How it started

> issues 33 and 120 are in need-triage. Does that make sense? How do they
> relate to the current issues?

## 2. Facts the AI looked up

- #33's plan ([grilling-33-playwright.md](../2/grilling-33-playwright.md))
  split it into #122–#126. #122–#125 are closed; #126 (test schema) is open
  as its own `needs-triage` follow-up. #33 stayed open because PR #127 closed
  #122, not #33.
- Every UI check in #33's checklist comment has a Playwright spec in
  `i03.d004-testing.md`.
- #120's body said Playwright "arrives this iteration with #33"; it already
  arrived with #122. Since then, `CorrectPickers`, `ResolveControl` and
  `BetForm` were added.
- The testing-policy record (PR #199, Q12) files later work as `needs-triage`
  Tasks with no estimate, like #195–#198 and #208. #202 excludes components
  from frontend coverage, pointing at #120. #186 covers pure `src/lib` modules.
- #183 (UI redo) will reshape the components #120 would test.
- Frontend CI does not install a browser; `e2e.yml` installs Chromium.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Close #33 | Close as completed, tick its checklist, comment mapping each check to its spec; #126 stays open | Yes |
| Q2 | #120 | (a) keep `needs-triage` as a deferred "Decide:" item, refresh the body; (b) fold into iteration 3 under #186; (c) `wontfix` | (a) and (b) |
| Q3 | Blocked by #183 | Record #183 as a blocker | Yes, later reversed by Q5 |

On Q2:

> Q2 (a), but I think we can decide now that it should be done, so (b) too?

## 4. Round 2

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q4 | Backlog placement | Sub-issue of #186, Iteration 3 board, assigned to Alef, no estimate | Yes, with an estimate |
| Q5 | Label | `ready-for-agent`, held by the #183 blocker | `ready-for-agent`, not blocked |
| Q6 | Which components | Every component with a branch; list settled after #183 | The rule, applied now |
| Q7 | CI | Frontend CI installs Chromium and runs component tests from the start | Yes |
| Q8 | Coverage | Components count toward coverage; undo #202's exclusion and update the #203 policy | Yes |

> Q4 yes but I think it should have an estimate. Q5 do we really need to wait
> on 183? I think we could write the tests and 183 deals with them. Q6 for
> start we can do that.

## 5. Round 3

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q9 | #183 and the tests | No blocker; comment on #183 that it updates #120's tests when it changes those components | Yes |
| Q10 | Estimate | 5 points (two Vitest projects, six components, CI browser, coverage) | Yes |
| Q11 | Recording it | Estimate field on the board and a line in `i03.d008-iteration-backlog.md`; #186 stays unestimated | Yes |

## 6. Outcome

- #33 closed with a comment mapping each check to its spec.
- #120 rewritten with acceptance criteria. It is a `Task`, labelled
  `ready-for-agent`, assigned to Alef, a sub-issue of #186, on the Iteration 3
  board with Estimate 5.
- #183 comment: either can land first; the redo keeps the component tests
  passing.
- No new glossary terms, no ADR.

Next step: a fresh session started with `/implement 120`.
