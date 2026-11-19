# Reply to the #121 review on where `lib/pool.ts` lives

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `grill-with-docs` skill from Matt
  Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** a
  [reply](https://github.com/MESW-LES-2627/les-project-group-8/pull/121#discussion_r4630918086)
  to the request to co-locate `pool.ts` and its test in `routes/pools/new`,
  and [#133](https://github.com/MESW-LES-2627/les-project-group-8/issues/133)
  to decide the layout for single-route frontend code.
- **Delegated:** reading the comment and the code; finding that
  `PoolForm.svelte` also imports the pool limits, that `routes/` holds only
  `+` files, that most `lib/components` serve one route, and that
  `account.ts` (`ce1bbec`) came in with no recorded reason; drafting the
  reply and the issue.
- **What we decided ourselves, and why:** keep `pool.ts` in `lib/` for this
  PR and move the layout question to its own issue, since it affects the
  whole frontend, not just tests. The reply calls the current layout what
  it is, an unwritten habit, instead of claiming `account.ts` was a
  deliberate precedent. Alef also pointed out that the reviewer's real
  complaint was where the tests were, which the first draft missed.
- **Where it was wrong:** the first draft cited `account.ts` as a precedent
  without checking why it was in `lib/`; once checked, it was only habit.
  Corrected in the posted reply.
- **Notes:** no glossary entry or ADR: file placement isn't domain language,
  and #133 decides whether the layout needs an ADR.
