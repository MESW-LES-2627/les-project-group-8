# Grilling session: overlapping stories in the iteration-2 retrospective

- **Date:** 2026-11-20, about 14:50 to 15:05 UTC.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the decisions below, for PR #168 (#162), to be split into
  tickets with `/to-tickets`.
- **Summary:** see the session entry
  [2026-11-20-1450Z-story-overlap-grilling.md](../../../iterations/2/ai-log/2026-11-20-1450Z-story-overlap-grilling.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> On pr 168. One thing we noticed was that user stories sometimes might have overlapped or acceptance criteria of one user story was itself another user story. How do you think we can introduce that in the retrospective

## 2. Facts the AI looked up

From `i02.d003-user-stories.md`, `i02.d008-iteration-backlog.md` and the
merged PRs:

- **Stories that are an AC of another story.** US18 (only the decider), US19
  (only after the deadline) and US20 (only once) are rules on US17 (resolve a
  Bet). US19 and US20 shipped in one PR, #98. Points: US17 2, US18 2, US19 1,
  US20 1.
- **A story with no code of its own.** US24's note says US22's leaderboard
  already lists every User with a Pick, so US24 adds only acceptance tests
  (PR #117, 1 point).
- **Repeated ACs.** US6.1 and 6.3 repeat US2.2 and 2.5; US23.1 repeats US17.2
  and US15.3; US16 is the reverse of US15.
- **Precedent.** US14 and US21 are already Obsolete, "Criteria incorporated
  into US10" and "into US17".

The AI did not check iteration 1's stories for the same pattern.

## 3. Decisions

1. **Where:** a paragraph in "What did not go well" of
   `i02.d009-retrospective.md`, and a matching item 3 in "Do differently".
2. **Examples:** cite US17 → US18–US20 (with #98 as evidence) and US24 (tests
   only). Leave out the smaller AC repeats (US6/US2, US23/US17, US15/US16).
   Mention that US14 and US21 were already folded back the same way.
3. **Throughput:** no recount. One sentence after the throughput figure: the
   16 points stand, since they were sized from merged PRs, but nine stories
   overstates the number of features.
4. **Do differently, item 3:** "At planning, before estimating, check each
   story against the others: if it only adds a rule or a failure case to
   another story, or shares its 'so that', make it an AC of that story (as
   done for US14 and US21)." It applies from iteration 3; the iteration-2
   backlog is not rewritten, so issue and PR links stay intact.

No glossary terms (process, not product) and no ADR (easy to reverse).

## 4. Where Alef changed the plan

Nowhere: Alef accepted every recommended answer ("Q1 yes. Q2 yes. Q3 yes. Q4
yes. Q5 yes"), then "go ahead".

## 5. Where the AI was wrong

Nothing found in the session.
