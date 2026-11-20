# See the correct pickers on a resolved Bet (US23)

- **Who:** Pedro Lunet.
- **Tools:** OpenCode (DeepSeek V4.1 Flash), `gh` CLI.
- **Outcome:** `lib/components/CorrectPickers.svelte`, mounted from
  `BetCard.svelte`, US23 marked Done in `i02.d003-user-stories.md`, and AC
  23.1–23.3 mapped in `i02.d004-testing.md`
  ([#81](https://github.com/MESW-LES-2627/les-project-group-8/issues/81),
  [PR #97](https://github.com/MESW-LES-2627/les-project-group-8/pull/97)).
- **Delegated:** writing the component and mounting it, updating the story and
  testing docs, running the frontend checks, and opening the PR.
- **What we decided ourselves, and why:** keep US23 frontend-only as planned:
  no new endpoint, no prop drilling of Picks through `BetCard`, and the
  component reads `page.data.picks` directly like `BetPicks`. Name the winning
  Outcome in the heading so the section reads on its own, and show an explicit
  empty state when nobody picked the winner.
- **Where it was wrong:** the first draft rendered for any Bet with a winner
  and took whichever Picks were loaded for the viewer. While the Pool is
  `OPEN`, `listPicks` returns only the viewer's own Picks, so the section would
  have claimed that only the viewer picked the winner. It is now gated on
  `Pool.status() == LOCKED`, a logged-in User and a successful Picks load.
- **How we checked:** `pnpm check` 0 errors and 0 warnings and `pnpm build`
  succeeds; no backend change, so the backend suite was not re-run. The
  two-Account browser check against a resolved Bet is still the remaining
  manual step.
- **Notes:** on 2026-11-20 the branch merged `staging` to clear the docs
  conflicts. `i02.d003` keeps staging's US22 `Done` and adds US23 `Done`;
  `i02.d004` keeps the E5 rows and adds AC 23.1–23.3; the retired
  `i02.d005-ai-log.md` takes staging's version, and this entry replaces the
  session record that had been appended to it.
