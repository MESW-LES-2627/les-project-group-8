# Grilling session: how we record AI usage

- **Date:** 2026-11-18 13:43 UTC to 2026-11-19 08:40 UTC.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the convention below, to be split into tickets with `/to-tickets`.
- **Summary:** see the session entry
  [2026-11-18-1343Z-ai-log-convention.md](../../../iterations/2/ai-log/2026-11-18-1343Z-ai-log-convention.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to talk about the way we've been recording ai logs so far. Is putting everything in one file really the best way? Are there refences out there on how to record ai usage? What are your suggestions? Also I was thinking to move to something that recorded one tier above what currently is being recorded, one tier more meagninful so I don't record literally every usage

## 2. Facts the AI looked up

- The log is one shared file per iteration (`iNN.d005-ai-log.md`), with
  roughly one entry per session. Iteration 1 has 10 entries in 144 lines, and
  the fields differ between team members.
- `docs/evaluation.md` scores "AI critique" (bound, 0–10). The 8–10 band:
  "Account shows assistance, not replacement. A key decision is human. One
  concrete miss, and the change is linked."
- `CLAIM.md` links the AI log at line 26. The highest document number in use is
  `d009`.
- References, in two families:
  - **Disclosure taxonomies from research publishing** record *how* AI was
    used, per output and by stage:
    [AID Framework](https://subjectguides.uwaterloo.ca/AIDFramework),
    [AI Usage Cards](https://arxiv.org/abs/2303.03886),
    [IBM AI Attribution Toolkit](https://www.research.ibm.com/blog/AI-attribution-toolkit),
    [GAIDeT](https://www.leidenmadtrics.nl/articles/gaidet-a-practical-taxonomy-for-declaring-ai-use-in-research-and-publishing).
  - **Code provenance** records *which lines* AI wrote: commit trailers
    ([Fedora](https://docs.fedoraproject.org/ca/council/policy/ai-contribution-policy/),
    [OpenInfra](https://openinfra.org/legal/ai-policy/); the Linux kernel
    [dropped its obligatory tag](https://www.theregister.com/ai-and-ml/2026/10/14/linux-kernel-devs-drop_obligatory_confession_of_ai_tool_usage/5303140)),
    and [Agent Trace](https://agent-trace.dev/) /
    [git-ai](https://usegitai.com/track-ai-code).
- A single shared file is the classic merge-conflict problem that changelog
  tools solve with one fragment file per entry
  ([towncrier](https://pyinstaller.org/en/stable/development/changelog-entries.html)).

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Is the per-iteration `d005` file a course requirement? | Treat it as required; change only what goes in it |
| Q2 | Which tier is the unit of an entry? | One per work item (GitHub issue/PR) |
| Q3 | What is the bar for an entry? | Log only if merged output, a changed decision, or a caught mistake |
| Q4 | Add `Assisted-by` commit trailers? | No new rule; rely on `Co-Authored-By` |

> Q1 we have no such template hard requirement, what's "required" is what is required to get the best grade as per evaluation.md . But sometimes I have grilling session that will result in sevaral issues. Q3 "writing this ai log" is definetly dropped, your suggestions sound prelimenarily sound. Q4 no co-authored-by, no assysted-by, we already assume any given commit might have AI usage at some point, what matters to know is how it was used

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q5 | Is the unit the parent work item, not the ticket? | One entry per feature (parent issue) |
| Q6 | Add a top "AI critique" summary per iteration? | Yes, answering the 8–10 band directly |
| Q7 | Fixed, shorter field set? | Yes, with a link to the fixing change for each miss |
| Q8 | Do earlier iterations stay as they are? | Leave i00/i01, restructure i02 |
| Q9 | Where does the convention live? | A header in each `d005` |

> Q5 I was looking for a more universal structure. Q6 yes, but it probably should go in a separate file right? Q7 yes, but how do wa take into account cases that don't fit this template? Q8 don't change what already was logged, we still haven't clarified the struture. I asked if putting everything in a giant AI log was a good idea and you didn't give an opinion, the giant file is a constant source of merge conflicts. Q9 before deciding where the convention lives, I wanted to know if there is any state of the art reference on how to log ai usage, but to answer your question, it would probably go under (a), but that's something I can't enforce for every team member, so it might be how I personally log my ai usage

The AI gave the opinion it had skipped: one shared file is bad for writing
and right for reading. It also searched for further references
(GAIDeT, IBM, Agent Trace, changelog fragments).

### Round 3

| Q | Question | AI recommended |
| :- | :- | :- |
| Q10 | Fragments plus a summary page? | One file per entry in `ai-log/`; `d005` becomes the summary |
| Q11 | Unit = one outcome? | One entry per outcome, tagged with stages |
| Q12 | Required core, optional fields, free notes? | Yes |
| Q13 | Fixed stage vocabulary? | Eight fixed software stages |

> Q10 I think using ai-log is misleading, we should have iNN.dNNN-ai-critique.md and slowly retire the ai-log. Q11 I'm thinking it might be better to log everything in a way that another pass over the log can make sense of the information and coalesce it into a more meagninful overview. Q12 agree. Q13 I think I won't use these references, I don't like fixed stages because ai varies a lot, what do you think?

The AI agreed to drop fixed stages: a later pass can find categories in what
actually happened.

### Round 4

| Q | Question | AI recommended |
| :- | :- | :- |
| Q14 | Two layers: raw session entries plus a critique built by a coalescing pass? | Yes; filtering moves from write time to the pass |
| Q15 | Raw entries in the repo as fragments? | Yes, committed with the work |
| Q16 | A grouping key? | Outcome required; links required when they exist |
| Q17 | Retirement path and number? | The critique takes the `d005` slot |

> Q14 yes, does it make sense to include artifacts in the repo such as the raw session log? Q15 yes. Q16 yes. Q17 We shouldn't have two equal iNN.dNNN documents, they should uniquely identify the resource

The AI advised against raw transcripts in the repo: they contain every tool
output (including `.env` reads), they are megabytes of JSON, and they exist only
for one tool.

### Round 5

| Q | Question | AI recommended |
| :- | :- | :- |
| Q17′ | Critique as a new number, `d010`? | Yes; `d005` retired, never reused |
| Q18 | Only curated transcripts committed? | Yes, under `docs/assets/`, checked for secrets |
| Q19 | Raw entry format and filename? | Bold-field Markdown, `YYYY-MM-DD-<slug>.md` |
| Q20 | Convention kept in Alef's personal setup? | Yes, nothing in the repo |

> Q17' yes. Q18 yes, only curated transcripts. Q19 yes, but shoudln't we include hour and minute in the timestamp? Q20 can we share this convention in the repo? How would we do it?

### Round 6

| Q | Question | AI recommended |
| :- | :- | :- |
| Q20′ | Share as `docs/ai-log.md` now, `AGENTS.md` line later? | (a) the doc only, for now |
| Q21 | Coalescing pass as a prompt in the doc, not a tool? | Yes |

> Q19 I prefer UTC. Q20' (b). Q21 yes

### Round 7

| Q | Question | AI recommended |
| :- | :- | :- |
| Q22 | How does the `AGENTS.md` line land? | A separate ticket blocked by PR #32 |

> Q22 That is false. staging already has AGENTS.md

The AI had looked only at `main`. `AGENTS.md` is on `staging` (`f3bf82b`), so
the line goes in the same ticket as `docs/ai-log.md`.

> go ahead. Remember that anything produced in this session needs to be included at some PR.

## 4. The decisions

- **Two layers.** Raw entries, one file per working session, at
  `docs/iterations/N/ai-log/YYYY-MM-DD-HHMMZ-<outcome-slug>.md` (UTC). The AI
  writes each at session end and the author reviews it. It is committed with
  the work. A session continuing the same outcome extends the same file.
  Sessions about the log itself are not logged.
- **Critique.** `iNN.d010-ai-critique.md`, built at iteration end by a
  coalescing pass over the raw entries (and any legacy `d005` entries), then
  edited by hand. It holds the tools and who used them, the key human decision
  and why, the concrete miss with its fix link, a verdict, and links to
  entries. CLAIM's row becomes "AI critique".
- **Entry fields.** Required: **Who**, **Tools**, **Outcome** (one line, with
  links whenever they exist), **Delegated** (free text, no fixed stages).
  Optional: **What we decided ourselves, and why**, **Where it was wrong**
  (each with a fix link), **How we checked**. **Notes** holds anything that
  doesn't fit.
- **Artifacts.** Only curated transcript excerpts under `docs/assets/`, when
  an entry cites them, after a check for secrets. Never raw transcripts.
- **Retirement.** `d005-ai-log` stays untouched in i00–i02. Its number is not
  reused.
- **Sharing.** `docs/ai-log.md` holds the convention and the coalescing
  prompt. A section in `AGENTS.md` points at it. Alef's memory points at it.
- **Not done.** No commit trailers, no fixed stages, no ADR (reversible), no
  glossary change (`GLOSSARY.md` is product language).

## 5. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q2/Q5 | One entry per issue, then per parent issue | A universal structure, not tied to GitHub |
| Q3 | Filter at write time | Log everything; a later pass coalesces it (Q11) |
| Q4 | Rely on `Co-Authored-By` | No trailers at all; what matters is how AI was used |
| Q6/Q10 | Summary at the top of `d005` | A separate `ai-critique` document |
| Q13 | Eight fixed stages | No fixed stages |
| Q17 | Reuse the `d005` slot | A new unique number, `d010` |
| Q19 | Date only, local time | Hour and minute, in UTC |
| Q20 | Personal convention, nothing in the repo | Shared in the repo and in `AGENTS.md` |

## 6. Mistakes and checks

- In round 1 the AI did not answer the question it was asked, whether one big
  file is a good idea. Alef pointed this out in round 2.
- In round 6 it said `AGENTS.md` only existed on the unmerged PR #32. It had
  checked a worktree based on `main`, which is behind `staging`.
- Not checked: whether the iteration 2 review has already happened. If it
  has, the critique starts in iteration 3.
