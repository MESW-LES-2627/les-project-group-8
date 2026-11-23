# End-to-end tests run against a throwaway local Supabase

For #33, the Playwright tests sign up Accounts and create Pools, Bets and Picks,
so they need a Supabase that is not production. They run against a local
Supabase started with the Supabase CLI (`supabase start`, in Docker), locally
and in CI. The stack is created for a run and thrown away after it, so no test
data ever reaches the shared project and nothing needs cleaning up.

The migrations stay in `backend/migrations/`. After `supabase start`, the e2e
setup applies every file there in sorted order with `psql`. The CLI's own
migration runner is not used: it skips `003a_…` and `003b_…`, whose names don't
match its `<digits>_name.sql` pattern, and adopting it would change how
production is migrated (by hand, in the SQL editor).

## Considered options

- **A second hosted Supabase project for tests:** not possible on the free tier,
  which the project already uses up.
- **The shared project, with a cleanup step:** rejected in #28. Test Accounts
  would land in production, and a crashed run would leave its data there.
- **A test schema in the shared project:** keeps Pools, Bets and Picks apart,
  but a project has one Auth, so test Accounts would still be created in
  production's `auth.users`, and the sign-up trigger would write their Users to
  `public.users`. It also needs a schema setting in Flask and the schema exposed
  in the API settings. Left as a follow-up issue to reconsider.

## Consequences

- Running the e2e tests needs Docker and the Supabase CLI.
- The local stack must sign tokens with ES256 signing keys, so Flask's JWKS
  check ([ADR 0001](0001-verify-supabase-tokens-locally.md)) and the frontend's
  `getClaims` behave as in production.
- Auth settings that production sets in the dashboard, such as email
  confirmation being off ([ADR 0002](0002-no-email-confirmation-for-the-demo.md)),
  must also be set in `supabase/config.toml`.
- A migration that fails on an empty database fails the e2e run, which also
  checks that the migrations still apply from scratch.
