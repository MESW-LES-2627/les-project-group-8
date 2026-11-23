# Grilling session: estimating iteration 2's stories after the fact

- **Date:** 2026-11-19 19:37 UTC to 2026-11-20 13:55 UTC.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the decisions below, to be split into tickets with `/to-tickets`.
- **Summary:** see the session entry
  [2026-11-19-1937Z-story-estimation-grilling.md](../../../iterations/2/ai-log/2026-11-19-1937Z-story-estimation-grilling.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> Our team did not estimate points for the stories at the start of the iteration. We are asked to do that for evaluation. What can we do?

## 2. Facts the AI looked up

- `docs/evaluation.md`, line 2 (User Stories, living): 5–7 is "Missing
  assignee, estimate, or acceptance-test link"; 8–10 needs "Estimated". A
  living line can still rise before the `iter-2` tag. Iter 3's theme
  expects honesty.
- No estimate exists anywhere: board 24 has no estimate field, and the "ACs"
  column of `i02.d003-user-stories.md` counts acceptance criteria, not points.
- Iteration 2 has nine `user-story` issues. Six are closed (#75–#78, #82,
  #84), three were open at the time (#79–#81). #135 (PR #136) changed US31's
  behaviour after US31 was done.
- Board 24 keeps every status change with a timestamp
  (`ProjectV2ItemStatusChangedEvent`). Time from first "In progress" or
  assignment to first "Done":

  | Story | Cycle time | Files | Diff | PRs | Reviews / comments | ACs |
  | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
  | US15 #75 | ~27 h | 14 | +131/−28 | #85 | 1 / 1 | 4 |
  | US17 #76 | ~22 h | 11 | +235/−4 | #89 | 1 / 0 | 5 |
  | US22 #77 | ~89 h (weekend) | 16 + 14 | +482/−211 | #90, #91 | 8 / 5 | 5 |
  | US18 #78 | ~90 h (weekend) | 5 + 7 | +224/−17 | #94, #95 | 4 / 1 | 3 |
  | US24 #82 | ~11 h | 9 | +199/−6 | #117 | 0 / 0 | 3 |
  | US31 #84 | ~11 h | 5 | +144/−7 | #118 (+ #136) | 1 / 0 | 5 |

- Caveats: every story was reset to "To do" and back on 11-19 at 17:26, and
  the close-on-staging workflows bounced some later, so only first
  transitions count. US22 skipped "In progress". Cycle time is calendar time
  (nights, weekend, review wait), not effort. US24 and US31 reused US22's
  Leaderboard.
- Commit timing does not measure effort either: authored times survive
  rebases, but US15 and US17 are single commits, and a span misses the work
  before the first commit.
- The organisation already has the issue types Task, Bug and Feature. Most
  technical work of iteration 2 (#66, #122–#125, #129, …) is not on board 24.
  GitHub's API cannot create project views.

## 3. Decisions

1. **Estimate now, and disclose it.** Rejected: presenting the points as made
   at planning (the field history would show otherwise), and not estimating.
2. **Scope:** the nine iteration-2 `user-story` issues. Not iteration 1 (its
   tag is scored) and not epics.
3. **Scale:** Fibonacci points 1, 2, 3, 5, 8; reference US22 = 3. An open
   story over 8 is split; a closed one over 8 is noted in the retrospective.
4. **Where:** a Number field `Estimate` on board 24, mirrored as a "Points"
   column, plus a "PRs" column, in `i02.d008-iteration-backlog.md`.
5. **Disclosure,** one sentence above that table: "Points were set on
   <date>, after the iteration started. Closed stories are sized from their
   merged PRs; open stories by analogy to them."
6. **How, closed stories:** ranked by judgment, not a formula, from cycle
   time, files, diff, PRs, reviews and AC count; review rework and files weigh
   most. US31's evidence includes #135 / PR #136. First read: US22 3, US18
   2–3, US17 2, US15 2, US31 2, US24 1.
7. **How, open stories:** by analogy to the closed ones, checked against AC
   count.
8. **Who:** Alef drafts all nine with a one-line reason each; the team
   approves in a PR.
9. **Technical work:** stories keep the `user-story` label; technical work
   gets issue type Task, defects issue type Bug. No "As a developer…" stories.
10. **Board:** board 24 stays the only board. A "Stories" view
    (`label:user-story`) is the one the claim links; a "Technical work" view
    (`type:Task,Bug`) holds the rest. Both made by hand in the UI. Closed
    iteration-2 Tasks and Bugs are added to the board and listed in a
    "Technical work" table in `i02.d008`, without points.
11. **From iteration 3:** stories, Tasks and Bugs are estimated at planning;
    story points and task points are reported separately. Every issue moves to
    "In progress" when work starts, so cycle time becomes reliable. No hour
    logging.
12. **Retrospective:** "Do differently" items "estimate at planning" and
    "In progress at start"; iteration-2 throughput reported, labelled
    retroactive, as the iteration-3 baseline.

No glossary terms (these are process terms, not product ones) and no ADR (all
easy to reverse).

## 4. Where Alef changed the plan

- **Blind planning poker, rejected.**

  > I don't like the blind poker thing. Can't we derive statistics from previous stories and how long it took to implement them? Also, why keep hindsight down? Shouldn't we take advantage of hindsight since we can get good data into the past on how long it actually took?

  The AI conceded: once the forecast is lost, hindsight is calibration, as
  long as the points are labelled as derived from actuals.

- **More data asked for.**

  > are there no other data? Can't we take when an issue was moved from open to in progress and then how long it took to get merged?

  > What other metrics do we have beside calendar time? Can't we time the commits?

  This led to the board history and the six-column table above.

- **Technical work and the board.**

  > Also, are we going to classify everything as user stories? How do we classify technical work? Where does that fit?

  > I think the board shouldn't include the tasks because it could pollute it, at least a separate view or something.

## 5. Where the AI was wrong

- It listed US24 (#82) and US31 (#84) as open from a snapshot taken at the
  start of the session and never rechecked it, though `i02.d003` already
  marked US31 Done. Alef caught it: "I think you missed some user stories
  done in this iteration."
- Its first answer on data said effort could not be recovered beyond PR
  timing; it had not looked at board 24's status history until Alef asked.
