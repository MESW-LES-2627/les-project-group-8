# Grilling session: find the current iteration board automatically

- **Date:** 2026-11-25.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` and `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the decisions below, applied in the same session (no ticket
  session); tracked as #193.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/3/ai-log/2026-11-25-0745Z-current-board.md).

Alef's messages are quoted word for word. The AI's questions are shortened to
their decision and its recommended answer.

## 1. How it started

> Why is issue 191 not showing up in the project board?

#191 had been added to board 24 (Group 8 — Iteration 2), not board 26
(Iteration 3), because `docs/agents/issue-tracker.md` hardcoded project 24 and
its field and option ids. The AI added #191 to board 26 and rewrote the doc to
look the board up.

> yes, do both. Can we make it know automatically the right project?

> I want to commit it and close boards 22 and 24 and open a PR

## 2. Facts the AI looked up

- The doc rewrite had already been committed by another session inside
  `f7aa0cf` (the default-assignee change), unpushed, on #191's branch
  (PR #192).
- Board 22 still held #31 and board 24 held #191, both `In review`; both
  issues are also on board 26.
- Board 26 has the same four views as board 24, with the story board at
  `views/1`.
- Three iteration-2 documents link to board 24; closed projects stay viewable.

## 3. Decisions

1. **Own PR off `staging`**, carrying only the board-lookup lines; `f7aa0cf`
   is left alone.
2. **A `Task` issue** (#193) on board 26, 1 point, closed by the PR.
3. **Close boards 22 and 24 now**, as they are: closed boards stay as a
   record, and anyone following the old doc hits a closed board instead of
   filing there silently.
4. **The views bullet is iteration-agnostic** ("Iteration N board").
5. **"Auto-add to project" is switched on at each iteration start**, by hand
   (UI only), as a row in the doc's table.
6. **Done in this session**: docs and GitHub metadata only. No ADR (easy to
   reverse, no real trade-off) and no glossary term (process vocabulary).
   > Q1 (a). Q2 yes. Q3 yes. Q4 yes. Q5 yes. Q6 yes
