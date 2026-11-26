# PR visual diff covers every screen

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills from Matt Pocock's Skills For Real Engineers.
- **Outcome:** Issue [#217](https://github.com/MESW-LES-2627/les-project-group-8/issues/217): `frontend/e2e/screens.showcase.ts` captures signup, the Pools list, new Pool, an open Pool, a closed Pool with resolved Bets, and its Leaderboard, from fixed Users, Pools, Bets and Picks created through the UI.
- **Delegated:** Wrote the spec and the optional fixed-account parameter on `signUp`. Ran two review sub-agents, one for standards and one for the spec, and applied part of their fixes.
- **What we decided ourselves, and why:** The closed Pool's deadline is moved into the past by a direct database write, because the UI and the backend reject a past deadline and the frozen browser clock doesn't reach the server. The Resolution itself goes through the UI. The helpers duplicated from `pools.spec.ts` stay duplicated for now; extracting them would mean rewriting that spec as well.
- **Where it was wrong:** The first draft named a screenshot `pool-resolved.png`, but the glossary says a Pool is never resolved. The standards reviewer caught it and the screenshot became `pool-closed.png`.
- **How we checked:** Ran the showcase five times through `run.sh`. Every image was identical except in one run, which failed because `/api/me` returned 401 straight after a sign-up. That is probably Docker Desktop's clock running ahead of the host's, so the token's `iat` looks like it is in the future. `pnpm check`, the unit tests (87) and the e2e suite (13) pass. The third acceptance criterion, a PR that changes one component, still needs a pushed PR.
