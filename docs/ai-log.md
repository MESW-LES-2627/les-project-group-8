# Logging AI usage

How we record how AI was used, so the team can write the iteration's AI
critique (line 10 of [`evaluation.md`](evaluation.md)) from evidence instead of
memory. The reasoning behind it:
[grilling-ai-log-convention.md](assets/iterations/2/grilling-ai-log-convention.md).

There are two layers:

1. **Raw entries.** One small file per working session, written cheaply, with
   no filtering. Anyone can add one without touching anyone else's file.
2. **AI critique.** One document per iteration, `iNN.d010-ai-critique.md`,
   drafted at iteration end from the raw entries by the
   [coalescing prompt](#coalescing-prompt), then edited by hand.

## Raw entries

### Where

`docs/iterations/N/ai-log/YYYY-MM-DD-HHMMZ-<outcome-slug>.md`

- `N` is the current iteration number (`2`, not `02`).
- The timestamp is when the session started, in **UTC**, followed by `Z`.
- `<outcome-slug>` is a few lowercase words, joined by hyphens, naming what the
  session produced.

Example: `docs/iterations/2/ai-log/2026-11-18-1343Z-ai-log-convention.md`.

A later session that continues the same outcome extends the same file instead
of starting a new one.

### When

At the end of every working session where AI was used. The AI drafts the entry,
the author reviews it, and it is committed with the work, on the same branch.

Sessions about the log itself (writing or fixing entries, running the
coalescing prompt) are not logged.

### Fields

A Markdown title naming the outcome, then a list of bold fields:

| Field | Required | What goes in it |
| :- | :- | :- |
| **Who** | yes | The team members who ran the session. |
| **Tools** | yes | Tools and models, with versions, plus any skills or prompts used. |
| **Outcome** | yes | One line: what the session produced. Link the issue, PR, commit or file whenever one exists. |
| **Delegated** | yes | Free text: what the AI did. No fixed list of stages. |
| **What we decided ourselves, and why** | no | Decisions a human made, especially where it overrode the AI. |
| **Where it was wrong** | no | Each mistake the AI made, with a link to the change that fixed it. |
| **How we checked** | no | Tests, reviews or manual checks of the AI's output. |
| **Notes** | no | Anything that doesn't fit above. |

Template:

```markdown
# <What the session produced>

- **Who:** <names>.
- **Tools:** <tool (model)>, <skills or prompts>.
- **Outcome:** <one line, with links>.
- **Delegated:** <what the AI did>.
- **What we decided ourselves, and why:** <optional>.
- **Where it was wrong:** <optional; each with a fix link>.
- **How we checked:** <optional>.
- **Notes:** <optional>.
```

A full example: [2026-11-18-1343Z-ai-log-convention.md](iterations/2/ai-log/2026-11-18-1343Z-ai-log-convention.md).

## Rules

- **Transcripts.** Never commit a raw session transcript: it holds every tool
  output, secrets included. When an entry needs evidence, commit a curated
  excerpt under `docs/assets/iterations/N/`, after checking it for secrets
  (keys, tokens, `.env` contents, passwords), and link it from the entry.
- **No log about the log.** Sessions about the AI log itself are not logged.
- **`d005-ai-log` is retired.** The existing `iNN.d005-ai-log.md` files in
  iterations 0–2 stay as they are. Don't edit them, and don't reuse the number
  `d005`.

## AI critique

At the end of each iteration, someone runs the prompt below with any coding
assistant, saves the draft as `docs/iterations/N/iNN.d010-ai-critique.md`
(for example `i03.d010-ai-critique.md`), and edits it by hand. `CLAIM.md` links
it as "AI critique".

### Coalescing prompt

```text
Draft this iteration's AI critique for our LES project.

Inputs:
- Every raw entry in docs/iterations/<N>/ai-log/.
- docs/iterations/<N>/i<NN>.d005-ai-log.md, if it exists (legacy format).
- The "AI critique" line in docs/evaluation.md, which says what reviewers look
  for.

Write docs/iterations/<N>/i<NN>.d010-ai-critique.md with these sections:

1. Tools: every tool and model used this iteration, and who used each.
2. Key human decision: the most important decision the team made itself
   rather than delegated, and why. Pick one; name others briefly if relevant.
3. A concrete miss: one specific place the AI was wrong, and a link to the
   change (commit or PR) that fixed it. Prefer a miss with a working link.
4. Verdict: a few sentences on how AI assisted the team this iteration,
   assistance rather than replacement, honestly stated.
5. Evidence: links to the raw entries (and legacy d005 entries) each claim
   comes from.

Rules:
- Use only what the entries say. Don't invent tools, decisions or misses.
- Every link must point at a file, commit or PR that exists. Check each one.
- Group by what actually happened; don't impose fixed stages.
- If the entries lack something a section needs, say so in that section
  instead of filling it.
```
