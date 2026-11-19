# Grilling session: end-to-end tests with Playwright (issue #33)

- **Date:** 2026-11-19.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** the plan below for
  [#33](https://github.com/MESW-LES-2627/les-project-group-8/issues/33),
  [ADR 0005](../../../adr/0005-e2e-tests-use-a-throwaway-local-supabase.md),
  and two follow-up issues to open.
- **Summary:** see the
  [raw AI-log entry](../../../iterations/2/ai-log/2026-11-19-1240Z-playwright-plan.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> I want to implement issue 33. I want it to be a gh stack on top of 121

## 2. Facts the AI looked up

- #33 asks for Playwright tests of sign up, log in, session restored after
  reload, expired session redirects to login, create a pool, and log out. A
  comment on it lists seven UI checks from the US31 plan: 2.11, US5, the
  pick/detail flow, 16.1–16.2, 24.1, 27.2 and 31.1–31.4.
- #121 (`alef/issue-67-vitest`) is the top of stack #115.
- Local, staging and production share one Supabase project (#28, Q21). That
  was why #28 put Playwright off.
- Flask verifies tokens with ES256 keys from the project's JWKS
  ([ADR 0001](../../../adr/0001-verify-supabase-tokens-locally.md)).
- Migrations live in `backend/migrations/` and are applied by hand in the SQL
  editor. The Supabase CLI's runner would skip `003a_…` and `003b_…`.
- `hooks.server.ts` renews an expired access token from the refresh token; a
  request is logged out only when renewal fails or the token's signature check
  fails.
- Not checked: the Supabase CLI isn't installed on this machine, so ES256
  signing on the local stack is unverified.

## 3. Round 1

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q1 | Branch and stack | `gh stack add alef/issue-33-playwright` on the #121 branch, PR 6 of stack #115; #120 later stacks on it | Yes |
| Q2 | Test database | (a) local Supabase via the CLI, thrown away per run; not (b) a second hosted project or (c) the shared project with cleanup | (a) (see below) |
| Q3 | Where it runs | Locally and in CI, in its own `e2e.yml` | Yes |
| Q4 | Scope | Setup, the six flows in #33, and 2.11, US5, pick/detail, 16.1–16.2, 27.2; 24.1 and 31.x to a follow-up | Yes |
| Q5 | Location and config | `frontend/e2e/*.spec.ts`, `frontend/playwright.config.ts`, Chromium only, `webServer` starts Flask and `vite preview` | Yes |

On Q2 Alef added:

> we can't have a second supabase project because we're in the free tier,
> however we could use the same supabase but create a separate "database" or
> schemas there for tests right? If so I might want to create a ticket to
> consider that option in the future.

The AI answered that a project can hold a test schema, but it has one Auth:
test Accounts would still land in production's `auth.users`, and the sign-up
trigger would write their Users into `public.users`. A schema keeps Pools, Bets
and Picks apart, not Accounts or Users. That limit goes into the follow-up
issue (Q10).

## 4. Round 2

| # | Decision | Recommended | Answer |
| :- | :- | :- | :- |
| Q6 | Migrations on the local stack | (a) keep `backend/migrations/`; apply each file in sorted order with `psql` after `supabase start`; not (b) move and rename them for the CLI | (a) |
| Q7 | Data isolation within a run | Each test signs up its own Accounts (`e2e-<random>@example.test`) and Pools; no reset between tests | Yes |
| Q8 | Expired session | Two specs: an expired access token with an invalid refresh token, and a forged signature; both expect `/pools/new` to land on `/login` | Yes |
| Q9 | ADR | ADR 0005, e2e tests run against a throwaway local Supabase | Yes |
| Q10 | Follow-ups | (1) checks that need a passed deadline: 24.1, 31.1–31.4, seeded through the database until #73; (2) consider a test schema in the shared project, with the Auth/Users limit | Yes |
| Q11 | Testing doc | `i02.d004-testing.md` rows for 2.11, US5, pick/detail, 16.1–16.2, 27.2 point at their specs; 24.1 and 31.x at follow-up (1) | Yes |

Defaults stated with the plan and approved with it ("go ahead"): the CI
triggers, no repo secrets, not a required check at first, ES256 checked first,
and no glossary change.

## 5. The plan

- Branch `alef/issue-33-playwright`, stacked on #121. PR body: "Closes #33.
  Stacked on #121."
- **First, check ES256.** Start the local stack with ES256 signing keys
  (`supabase gen signing-key`, `[auth] signing_keys_path`), and confirm that
  `/auth/v1/.well-known/jwks.json` serves them and that Flask's
  `TokenVerifier` and the frontend's `getClaims` accept a local token. If they
  don't, stop and come back to this plan.
- `supabase/config.toml`: signing keys, and email confirmation off as in
  [ADR 0002](../../../adr/0002-no-email-confirmation-for-the-demo.md).
- A setup script that runs `supabase start`, then applies
  `backend/migrations/*.sql` in sorted order with `psql`, and exports the URL
  and keys from `supabase status -o env` for Flask and the frontend.
- Playwright as a frontend dev dependency; `frontend/playwright.config.ts`,
  Chromium only, `webServer` starting Flask and `vite preview`; specs in
  `frontend/e2e/*.spec.ts`; a `test:e2e` script.
- Specs, each test with its own Accounts and Pools:
  - sign up; log in; session restored after reload; log out;
  - expired session: expired access token with an invalid refresh token, and
    a forged signature, both sent from `/pools/new` to `/login`;
  - create a pool; 2.11, the create-pool page sends a logged-out visitor to
    login and back;
  - US5, the header shows who I am;
  - pick/detail: an empty Pool, a radio Bet and a dropdown Bet, Picks on
    both, reload, change one without the other, then a second User sees
    neither the first User's Picks nor the authoring controls;
  - 16.1–16.2, before the deadline other participants' Outcomes are hidden and
    mine is shown;
  - 27.2, a dropdown Bet shows its ordered Outcomes in a labelled dropdown
    with none selected.
- `.github/workflows/e2e.yml`: on PRs touching `frontend/**`, `backend/**`,
  `supabase/**` or the workflow; installs the CLI with `supabase/setup-cli` and
  the Chromium browser; no repo secrets; not a required check at first.
- `i02.d004-testing.md` as in Q11; `frontend/README.md` says how to run the
  e2e tests.
- Out of scope: 24.1 and 31.1–31.4 (follow-up 1), the test schema (follow-up
  2), and component tests (#120).
