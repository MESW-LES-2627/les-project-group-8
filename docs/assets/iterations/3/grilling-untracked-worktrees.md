# Grilling session: untracked worktrees and stale worktree entries

- **Date:** 2026-11-25.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below, filed as
  [#191](https://github.com/MESW-LES-2627/les-project-group-8/issues/191).
- **Summary:** see the
  [raw AI-log entry](../../../iterations/3/ai-log/2026-11-25-0726Z-untracked-worktrees.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I see many changes vs origin. It seems all worktrees are shown. Why is that?

The AI found that `staging` was 0 ahead and 0 behind `origin/staging`. The
"changes" were untracked files: `.claude/worktrees/` is not ignored, so the
diff view listed every file of every worktree checkout. `.idea/` and
`backend/.idea/` showed up for the same reason.

> I want to fix that

## 2. Facts the AI looked up

- `.claude/` is partly committed (`.claude/skills/vision-board-review/`), so
  the team shares that folder.
- `.claude/worktrees/` holds 10 folders:
  - 3 still linked to Git (`ai-log-changes`, `issue-104`, `issue-82`), with no
    uncommitted changes. Their branches' PRs (#114, #110, #169) are merged.
  - 7 disconnected (`alef+test-rls-back-door`, `auth-review-fixes`,
    `issue-35-auth-me`, `issue-36-rls`, `issue-37`, `issue-38`, `issue-39`).
    Each folder's `.git` file still points into the repo's old location
    (`FEUP - MESW/Unidades Curriculares/...`), so Git can't read their status.
    Their last commits are all on origin.
- `git worktree list` also lists folders that no longer exist: 4 old
  scratchpad paths and `les-project-group-8-worktree-01`. Some paths appear
  twice, once per Unicode spelling of "Laboratório".
- `alef/test-rls-back-door` is locked. Its PR #43 is merged.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Where the ignore rule goes: committed `.gitignore`, or this machine's `.git/info/exclude` | `.gitignore`, adding `.claude/worktrees/` and `.idea/` | (a), `.gitignore` |
| Q2 | Delete all 10 worktree folders | Yes: `git worktree remove` the 3 linked ones; delete the 7 disconnected ones only after comparing each folder's files with its last commit, keeping and reporting any that differ | Yes |
| Q3 | Clear stale worktree entries | Yes: unlock `alef/test-rls-back-door`, run `git worktree prune`, keep local branches | Yes |
| Q4 | Leave the other untracked files out of scope | Yes | Yes, with a question |
| Q5 | No ADR and no glossary changes | Yes | Yes |

Q4's question:

> why is `docs/assets/iterations3/` untracked?

A parallel session had written `docs/assets/iterations/3/grilling-docs-link-check.md`
and its AI-log entry, and committed both as `f0ebfe3` on the pushed branch
`docs-link-check` while this session ran. Nothing was lost.

## 4. The plan

1. Add `.claude/worktrees/` and `.idea/` to `.gitignore`. The `.idea/` line
   also covers `backend/.idea/`.
2. Remove the 3 linked worktrees with `git worktree remove`.
3. For each of the 7 disconnected folders, compare its files with its last
   commit. Delete the folders that match; keep and report any that differ.
4. Unlock `alef/test-rls-back-door`, then run `git worktree prune`. Local
   branches stay.
5. Out of scope: the Nuno evaluation PDF and the WhatsApp chat zip stay
   untracked.
6. No ADR and no glossary changes: the change is easy to reverse and names no
   domain terms.

Steps 2 to 4 are local cleanup on Alef's machine; only step 1 is committed.

> go ahead
