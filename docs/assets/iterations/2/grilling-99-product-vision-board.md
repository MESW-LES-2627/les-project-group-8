# Grilling session: Product Vision Board (PR #99)

- **Date:** 2026-11-18.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below, split by `/to-tickets` into
  [#101](https://github.com/MESW-LES-2627/les-project-group-8/issues/101),
  [#102](https://github.com/MESW-LES-2627/les-project-group-8/issues/102),
  [#103](https://github.com/MESW-LES-2627/les-project-group-8/issues/103) and
  [#104](https://github.com/MESW-LES-2627/les-project-group-8/issues/104).
- **Summary:** see "Planning the Product Vision Board changes to PR #99" in the
  [iteration 2 AI log](../../../iterations/2/i02.d005-ai-log.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to propose changes to pr 99. I want to convert the table into headings
> so it's easier to read and edit. I also want to fix the terms so they match
> the glossary. I also want to reference the board against Richard Pichler
> source material so we can easily argue that it's correct.

[PR #99](https://github.com/MESW-LES-2627/les-project-group-8/pull/99), by João
Luiz Cerqueira, rewrites `docs/iterations/2/i02.d001-vision.md` on branch
`refine-product-vision` with a Product Vision Board as a single Markdown table.

## 2. Facts the AI looked up

- The author is **Roman** Pichler.
- Alef's earlier review on #99 lists the glossary drift: "predictions" for
  Picks, "results" for Resolutions and the Leaderboard, "referees" for the
  Decider, undefined "organizers"/"participants".
- Decider, Resolution, Record and Leaderboard are defined only in the
  `staging` glossary.
- The course rubric (`docs/evaluation.md` §1) asks for the five board fields:
  vision, target group, needs, product, business goals.
- *Agile Product Management with Scrum* (Pichler, 2010) is the only Pichler
  book found at first; it predates the board.
- *Strategize* (Pichler) defines the board in the section "Capture Your
  Strategy with the Product Vision Board": five sections, vision, target group,
  needs, product and business goals.
- [The article](https://www.romanpichler.com/tools/product-vision-board/)
  does not define the blocks one by one. Its only line on contents is "It
  captures the target group, needs, key features, and business goals."
- [The board PDF](https://www.romanpichler.com/downloads/tools/Product-Vision-Board-with-Checklist.pdf)
  has a guiding question per block, under CC BY-SA 4.0. Its checklist pages
  are "© 2024 Roman Pichler", with no CC licence.
- The repository is public.

## 3. Questions and answers

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | How to propose the changes | (a) A PR into `refine-product-vision` |
| Q2 | Heading structure | Five `###` blocks in Pichler's order, Vision moved inside, sentence case |
| Q3 | Content under each heading | Bullets, needs by priority, drop `<ins>`; Feasibility only with a link |
| Q4 | Term mapping | Picks; Decider resolves Bets / Resolutions; Leaderboard; "a Decider other than the Pool's creator"; lowercase templates/rounds |
| Q5 | "Organizers" and "participants" | (a) Use the Pool's creator (its Decider) and Users; no new glossary terms |
| Q6 | "Weighted scoring" | Rephrase to "Bets worth different amounts" |
| Q7 | Which Pichler source | (a) The romanpichler.com article |
| Q8 | Where the references go | (b) One source note plus a References list |
| Q9 | Scope | Headings, terms and references only, plus the repeated sentence |

> Q1 (a). Q2 yes. Q3 yes. Q4 yes. Q5 (a). Q6 yes. Q7 cite the article. I also
> want to create a template from this pdf
> /Users/alef/Downloads/Product-Vision-Board-with-Checklist.pdf and an ai skill
> to rate our vision board according to the criteria described there, we can
> reference the pdf too, it can be found at
> https://www.romanpichler.com/downloads/tools/Product-Vision-Board-with-Checklist.pdf.
> Also you can cite Strategize, locally I have it here
> /Users/alef/Downloads/strategize.pdf  we should add untracked to the repo so
> you can reference it. Q8 (b) but with (a) style, so each block gets a short
> quote with a link. Q9 yes, the focus should be on having a product vision
> board according to Pichler.

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q10 | Source of the per-block quotes | The board PDF's guiding questions, verbatim and linked; article, PDF and *Strategize* in References |
| Q11 | Where the local sources live | `docs/books/`, gitignored; no bib file |
| Q12 | Template | `docs/templates/product-vision-board.md`, blank five-block skeleton, CC BY-SA 4.0 attribution |
| Q13 | Skill location and name | Repo-scoped `.claude/skills/vision-board-review/`, Pichler only |
| Q14 | What the skill reports | Met / Partly / Not met per criterion, evidence sentence, fix; edits nothing; no 0–10 score |
| Q15 | Overall criteria | Connected from the MVP link, Adaptive from git history; Validated, Shared, Needs-first unverifiable without evidence |
| Q16 | How the skill carries the checklist | Criterion names plus a paraphrase, PDF linked |
| Q17 | PR split | Two PRs: board into `refine-product-vision`, template and skill into `staging` |

> Q10 yes. Q11 yes. Q12 yes. Q13 yes. Q14 yes. Q15 yes. Q16 I want the
> criteria verbatim based on what is in the PDF. Q17 yes.

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q18 | Where the verbatim checklist lives, given a public repo and a non-CC checklist | (a) Read it from the PDF at run time; commit only the names |

> Q18 (b).

The AI then restated the plan and asked for confirmation.

> yes

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q7 | Cite the article | Cite the article, the board PDF and *Strategize*; also make a template and a rating skill from the PDF |
| Q8 | One source note plus References | References list, and a short linked quote under each block |
| Q16 | Criterion names plus paraphrase | Criteria verbatim from the PDF |
| Q18 | Read the checklist at run time | (b) Commit the checklist verbatim in `SKILL.md`, with © attribution and a link |

All other recommendations were accepted as given.

## 5. The plan

**PR A → `refine-product-vision`** (`docs/iterations/2/i02.d001-vision.md`)

- `## Product Vision Board` with `### Vision`, `### Target group`, `### Needs`,
  `### Product`, `### Business goals`; the standalone Vision section moves
  inside.
- Each block opens with Pichler's guiding question from the board PDF,
  verbatim, linked to the PDF.
- Bullets instead of bold labels; needs ordered by priority; `<ins>` removed;
  Feasibility kept only with an evidence link.
- Glossary terms: Picks; the Decider resolves Bets; Resolutions; Leaderboard;
  "a Decider other than the Pool's creator"; lowercase templates and rounds;
  "Bets worth different amounts"; no "organizers" or "participants". The
  repeated "creator records winning Outcomes" sentence is said once.
- A References list: the article, the board PDF, and *Strategize* ("Capture
  Your Strategy with the Product Vision Board").
- Nothing else changes; the other review findings stay on #99.

**PR B → `staging`**

- `docs/books/` in `.gitignore`; `strategize.pdf` and the board PDF kept
  there locally.
- `docs/templates/product-vision-board.md`: the blank five-block skeleton
  with the linked guiding questions and CC BY-SA 4.0 attribution.
- `.claude/skills/vision-board-review/SKILL.md`: report only, Pichler's
  checklist verbatim with "© 2024 Roman Pichler" and a link. For each
  criterion: Met / Partly / Not met, the board sentence it rests on, a fix.
  Connected is judged from the MVP link, Adaptive from git history;
  Validated, Shared and Needs-first are unverifiable without linked evidence.

No glossary change and no ADR: none of these decisions is hard to reverse.

**Tickets** (`/to-tickets`, approved as proposed, labelled `ready-for-agent`,
kept off the Iteration 2 board because they are not user stories):

| Ticket | Blocked by |
| :- | :- |
| [#101](https://github.com/MESW-LES-2627/les-project-group-8/issues/101) Product Vision Board template, with local Pichler sources | — |
| [#102](https://github.com/MESW-LES-2627/les-project-group-8/issues/102) `vision-board-review` skill | — |
| [#103](https://github.com/MESW-LES-2627/les-project-group-8/issues/103) Restructure the PR #99 vision board to Pichler's blocks | #101 |
| [#104](https://github.com/MESW-LES-2627/les-project-group-8/issues/104) Rate the restructured board and post the result on #99 | #102, #103 |

The template and the skill get one PR each into `staging`, not the single PR B
planned above.

## 6. Mistakes and checks

- The AI first recommended citing the article for each block, before checking
  what it says. Fetching it showed it does not define the blocks, so the
  per-block quotes come from the board PDF instead.
- Alef's global `citation-check` skill expects `report/references.bib`, which
  this repo lacks, so citations are checked by hand for now.
- Not checked: whether a vision-slice evidence link for Feasibility exists.
