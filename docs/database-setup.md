# PostgreSQL setup for issue 31

The backend uses Psycopg for Users, Pools/Bets and Picks. PostgreSQL remains on
Supabase. Login, ES256 token verification, the signup trigger, RLS and all
frontend authentication code from staging are retained.

## Local application and staging

1. Install `backend/requirements-dev.txt`. Set `DATABASE_URL` in `backend/.env`
   from Supabase **Connect**, using the actual database password (URL-encoded),
   not an API key. The session pooler on port 5432 supports IPv4; include
   `sslmode=require`. Prepared statements are disabled for transaction-pooler
   compatibility. The role must own the application tables or have `BYPASSRLS`,
   because Flask enforces access and the tables deliberately have no RLS policies.
2. Keep `SUPABASE_URL` for the Auth signing keys. The frontend keeps its existing
   `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` and `API_URL`. Use the same Supabase
   project for Auth and the connected database so a token's User exists there.
   `SUPABASE_KEY` is no longer used by runtime repositories.
3. A new Supabase database applies 001, 003, 003a, 003b, 004,
   `20261104210948_pool_contains_bets.sql`, then
   `20261105000100_pool_transactions.sql`. Historical 002 is optional and
   superseded. An up-to-date staging database needs only the last migration.
   Run complete migration files in the SQL Editor or `psql -v ON_ERROR_STOP=1`.
   Migration 003b has the team's existing guest-removal behavior; do not rerun
   old migrations on an initialized project.
4. Coordinate the last migration with backend deployment: it makes
   `bets.round_id` mandatory, so the old writer cannot add Bets afterwards.
   It backfills one internal round per existing Pool without replacing Bet,
   Outcome or Pick IDs. It does not add a round-management API or UI.
5. Run `flask --app app run --port 5001` and the existing `pnpm dev` frontend.
   Use the application's signup/login flow. The guest ID is no longer accepted.
   Check `GET /api/pools` as well as `/api/health`: health is only Flask liveness.

In Render set `DATABASE_URL` and retain `SUPABASE_URL` on
`les-backend-staging`; `render.yaml` declares both with `sync: false`. Keep the
connection URI server-only. The current project shares one Supabase instance
between environments, so coordinate schema changes with the team. Separate
projects are supported but are not provisioned by this change.

After deploying to staging, log in at the staging frontend, create a Pool, add a
Bet, save/change a Pick, then refresh both detail and list pages. Record the
commit and result in the PR. Deployment and teammate review are still required
for the complete Definition of Done.

## Atomic operations

The existing empty-Pool frontend flow is unchanged. API callers can also send:

```json
{
  "name": "Final",
  "deadline": "2030-06-01T18:00:00Z",
  "initial_bets": [
    {"statement": "Home wins?", "options": ["Yes", "No"]}
  ]
}
```

Use the existing Bearer access token. The logged-in User is the creator/decider.
The Pool, one initial round, initial Bets (questions) and options share one
transaction. Omitting `initial_bets` creates an empty Pool and its initial round.
`POST /api/pools/{id}/bets` also saves its Bet and options in one transaction;
failure performs no cleanup DELETE and leaves existing Bets and Picks intact.
The existing option count, presentation, ownership and deadline rules still apply.

## Real PostgreSQL tests

From the repository root in PowerShell:

```powershell
docker compose -f compose.test.yaml up -d --wait
$env:TEST_DATABASE_URL = 'postgresql://les:les@127.0.0.1:55433/les_test'
cd backend
.\.venv\Scripts\python.exe -m pytest -v
```

On macOS/Linux use `export TEST_DATABASE_URL=...` and `.venv/bin/python -m pytest -v`.
The test role needs `CREATEDB` and permission to create the `service_role` role
if absent; the isolated Docker service and CI role provide this. Tests create
randomly named databases, run the real Supabase migrations against a minimal
test-only Auth table, verify ES256 tokens with a throwaway key, and drop only
their generated databases. They never use runtime `DATABASE_URL` as a fallback.
They do not test the hosted Supabase signup service itself.

A test-only SQL trigger fails option insertion after successful earlier writes.
Tests compare full snapshots of Pools, rounds, Bets, options, Users and Picks,
then send another valid request and read its committed result. They also cover
Pick replacement and preservation of existing IDs/results during migration.
Without `TEST_DATABASE_URL`, these tests skip; CI always supplies a PostgreSQL 17
service and the test URL. Existing remote RLS tests remain separate and use the
publishable key. `supabase` is retained only in development requirements for them.

Stop the test service afterwards from the repository root:
`docker compose -f compose.test.yaml stop`.

## Verification after integration

On 2026-11-05, after merging staging `c91ad47`, all 114 backend tests passed,
including PostgreSQL rollback and the existing remote Supabase RLS tests.
Frontend type checks and production build passed. A local HTTP form check covered
login, Pool creation, adding a dropdown Bet, saving/replacing a Pick and refreshing
detail/list pages, using real PostgreSQL and a temporary ES256 Auth test server.
Hosted Auth and a deployment of this branch to staging still need verification.
