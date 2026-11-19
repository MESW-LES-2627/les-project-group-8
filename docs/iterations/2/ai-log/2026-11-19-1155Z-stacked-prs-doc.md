# A guide to stacked PRs for agents

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `retro` and
  `writing-for-agents` skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** `docs/agents/stacked-prs.md` and a pointer to it in `AGENTS.md`.
- **Delegated:** reading the session logs for stack #115 (#82 and #84), finding
  where `gh stack` failed, proposing fixes, and writing the doc.
- **What we decided ourselves, and why:** to apply every fix the retro proposed.
  The `.DS_Store` clean-up is a hook in Alef's own Claude Code settings, not the
  repo, because only his Mac creates the file.
- **Notes:** the two failures were a Finder `.DS_Store` in `.git/worktrees`
  that broke every local `gh stack` command, and an agent editing
  `.git/gh-stack` by hand instead of running `gh stack link`.
