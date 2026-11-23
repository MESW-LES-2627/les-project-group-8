# A convention for recording AI usage

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** an agreed convention for logging AI usage: raw session entries
  in `ai-log/` plus a per-iteration `d010-ai-critique.md`. Record:
  [grilling-ai-log-convention.md](../../../assets/iterations/2/grilling-ai-log-convention.md).
- **Delegated:** reading the existing logs and `docs/evaluation.md`; searching
  for published references on recording AI use (AID, AI Usage Cards, GAIDeT,
  IBM's toolkit, commit trailers, Agent Trace, changelog fragments); asking
  seven rounds of questions with recommended answers; writing the session
  record and this entry.
- **What we decided ourselves, and why:** log every session cheaply and let a
  later pass build the meaningful overview, instead of filtering at write time.
  No fixed stages, because AI use varies too much. A unique `d010` number for
  the critique, since a document number must identify one resource. Timestamps
  in UTC. Share the convention in the repo and in `AGENTS.md` rather than keep
  it personal.
- **Where it was wrong:** it skipped the question of whether one big file is a
  good idea until asked again. It said `AGENTS.md` only existed on PR #32,
  having checked a branch based on `main` instead of `staging`. Both were
  corrected in the session (see the record, section 6).
- **Notes:** this is the first entry in the new format, written before
  `docs/ai-log.md` exists.
