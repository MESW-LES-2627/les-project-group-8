# Fixed broken repo links in PR bodies

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5).
- **Outcome:** Rewrote relative doc links in PRs #107, #113, #117, #118, #121, #127, #192, #194, #206, #207, #209 and #213 to absolute `blob/<sha>` URLs, and added a link rule to [`docs/agents/issue-tracker.md`](../../../agents/issue-tracker.md).
- **Delegated:** Found why the links opened GitHub's empty compare page (relative paths resolve against `/pull/`), found the affected PRs, rewrote and re-uploaded their bodies, and wrote the docs rule.
- **How we checked:** Confirmed each target file exists at the PR's head SHA through the GitHub API, then re-listed the last 60 PRs and found no relative links left.
- **Notes:** Only the last 60 PRs were checked. Issue bodies and comments were not.
