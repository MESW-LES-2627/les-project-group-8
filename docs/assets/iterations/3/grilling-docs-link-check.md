# Grilling session: stopping dead links in the docs

- **Date:** 2026-11-24 17:50 UTC to 2026-11-25 07:15 UTC.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below, to be split into tickets with `/to-tickets`.
- **Summary:** see the session entry
  [2026-11-24-1750Z-docs-link-check.md](../../../iterations/3/ai-log/2026-11-24-1750Z-docs-link-check.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

A handoff from an earlier session. It proposed a rule in
[`ai-log.md`](../../../ai-log.md) and a CI job, both to stop dead links in raw
AI log entries. The trigger was
[PR #174](https://github.com/MESW-LES-2627/les-project-group-8/pull/174): its
entry `2026-11-23-1157Z-iteration-3-planning.md` linked to two sections that
had been deleted by hand. Both files still existed, so only a checker that
reads `#anchors` would catch it. Per [`evaluation.md`](../../../evaluation.md),
a dead link from the claim caps that line at 4.

## 2. Facts the AI looked up

All on `origin/staging`, with lychee 0.24.2:

- There was no link checker in `.github/workflows/` or in any `package.json`.
  The workflows pin actions to major tags (`actions/checkout@v4`).
- `lychee --offline --include-fragments 'docs/**/*.md'` finds one dead link:
  `docs/iterations/2/i02.d003-user-stories.md:560` points to
  `../../diagrams/DomainModel.puml`. That file now exists only under
  `docs/diagrams/0/` and `docs/diagrams/1/`.
- The same command on `origin/iteration-3-planning` reports both PR #174
  anchors as `Cannot find fragment`.
- GitHub-style anchors with an em dash, such as
  `#us28-create-and-answer-an-open-ended-bet--next`, resolve.
- Docs link into code (`backend/migrations/*.sql`, `frontend/src/...`), so a
  code-only change can break a docs link.
- `CLAIM.md` links to `https://github.com/.../blob/iter-N/...`, a tag that
  doesn't exist until review. `--offline` skips these full URLs. With
  `--remap 'https://github\.com/MESW-LES-2627/les-project-group-8/(blob|tree)/iter-[0-9.]+/?(.*) file://<root>/$2'`
  they are checked against the local tree: a planted
  `blob/iter-3/.../i02.d002-mvp.md#nope` failed, and all three existing claims
  passed.

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Which files does the check scan? | Every Markdown file (`'**/*.md'`), excluding `node_modules` and `.claude/worktrees` |
| Q2 | Run on every PR, or filter on `docs/**`? | Every PR, no paths filter |
| Q3 | Fix the existing dead link? | Yes, in the same PR, pointing at `diagrams/0/` (the vision model) |
| Q4 | Local lychee run: required or best-effort? | Best-effort; CI is the guarantee |
| Q5 | Make the check required in this work? | No; the job only, advisory |
| Q6 | Who fixes the PR #174 entry? | Its author, in #174 |
| Q7 | Rule for raw entries only, or the AI critique too? | Shared "Rules" section, covering both |

> Q1 agree. Q2 agree. Q3 yes. Q4 agree. Q5 agree. Q6 yes. Q7 agree. What should we do about links in CLAIM.md that point to a release before we tag it?

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q8 | How are tag permalinks in `CLAIM.md` checked? | `--remap` them to the checked-out tree in the PR job |
| Q9 | Who checks external claim links (compare, actions, board, deploy URLs)? | Nobody new; step 2 of `evaluation.md` already opens every permalink |

> Q8 (b). Q9 yes

> confirm

### Round 3

After the plan was confirmed, the AI found that PR #174 had already merged,
so its two dead anchors were on `origin/staging` and Q6 could no longer
happen.

| Q | Question | AI recommended |
| :- | :- | :- |
| Q10 | Fix the two PR #174 anchors in the link-check PR? | Yes, point them at the whole files, so the check starts green |

> Q10 yes

## 4. The decisions

1. **Rule.** One **Links** rule goes under the shared "Rules" in
   `docs/ai-log.md`, covering raw entries and the AI critique. The coalescing
   prompt's "every link must exist" line points to it. The rule says:
   - Write the entry last, after the session's files are final, hand edits
     included.
   - Link to things that won't move: a PR, issue, commit or whole file.
   - Use a `#section` only if that heading is on your branch.
   - Run `lychee --offline --include-fragments <file>` if you have it
     installed; otherwise CI catches it.
   - Whoever deletes or renames a heading fixes the links to it.
2. **CI.** A new `.github/workflows/docs-links.yml`:
   - Runs on `pull_request`, with no paths filter.
   - Checks `'**/*.md'`, excluding `node_modules` and `.claude/worktrees`.
   - Uses `lychee --offline --include-fragments`.
   - Remaps our `blob|tree/iter-N` permalinks to the checked-out tree, so
     claim links are verified before the tag exists.
   - Pins actions to major tags, as the other workflows do.
3. **External claim links** stay out of CI. Step 2 of `evaluation.md` covers
   them by hand.
4. **The existing dead links** are fixed in the same PR, so the check starts
   green:
   - `i02.d003-user-stories.md:560` will point to
     `../../diagrams/0/DomainModel.puml`.
   - Line 14 of `iterations/3/ai-log/2026-11-23-1157Z-iteration-3-planning.md`,
     merged with PR #174, drops its two dead anchors and links to the whole
     files.
5. **Out of scope:** making the check required, which is a separate decision.
6. **Delivery:** one branch from `origin/staging`, one PR to `staging`.

There's no ADR and no glossary term: all of this is cheap to reverse, and none
of it is domain vocabulary.

## 5. Where Alef changed the plan

- The handoff left `CLAIM.md` tag links to a hand check. Alef's question about
  them led to the `--remap` option, which checks them in CI before tagging.

## 6. Mistakes and checks

- Q6 assumed PR #174 was still open. A check after the plan was confirmed
  showed it had merged; Q10 replaced it.

- The first lychee run extracted only `docs/`, so every link into code showed
  as dead (31 errors). Re-running on the full tree left one real error.
- The remap was tested only locally. In the Action, `<root>` becomes
  `${{ github.workspace }}`, and the PR's first CI run confirms it.
