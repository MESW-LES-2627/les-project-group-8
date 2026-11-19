# A plan for end-to-end tests with Playwright

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `grill-with-docs` skill
  (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Outcome:** an agreed plan for
  [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33),
  stacked on #121, and
  [ADR 0005](../../../adr/0005-e2e-tests-use-a-throwaway-local-supabase.md).
  Record:
  [grilling-33-playwright.md](../../../assets/iterations/2/grilling-33-playwright.md).
- **Delegated:** reading #33 and its UI-check comment, #121's stack, the #28
  grilling, ADR 0001, the migrations, the Render config and the session hook;
  noticing that the CLI skips `003a`/`003b` and that an expired access token is
  renewed rather than redirected; asking two rounds of questions with
  recommended answers; creating the stacked branch; writing the ADR, the
  record and this entry; with `/to-tickets`, splitting the plan into
  sub-issues #122–#126 of #33 with native blocking edges, and making #120
  blocked by #122.
- **What we decided ourselves, and why:** a second hosted Supabase project is
  ruled out by the free tier. Alef raised a test schema in the shared project
  as a future option; it becomes a follow-up issue, noting that it still shares
  Auth.
- **How we checked:** read the code paths the plan relies on; nothing was run.
  ES256 signing on the local Supabase stack is unverified and is the first
  implementation step.
