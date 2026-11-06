# Flask is the only way into the app tables

Row-level security is enabled on `users`, `pools`, `outcomes` and `picks` with **no policies**, so Supabase's REST API refuses every direct read and write made with the publishable key or an Account's token. Flask connects with the secret key, which bypasses RLS, and enforces who may do what in its services. We chose this because the publishable key is public by design (one was even committed in `backend/.env.example`): without RLS, anyone holding it could insert a pool with someone else's `creator_id` and skip Flask's impersonation checks entirely.

## Considered Options

- **RLS policies per table** (e.g. `creator_id = auth.uid()`), letting the frontend talk to Supabase directly: splits the business rules between SQL policies and Python services, and the architecture already routes everything through Flask.

## Consequences

Update for #31: Flask now uses Psycopg and `DATABASE_URL`, with a PostgreSQL
table-owner or `BYPASSRLS` role, instead of the Data API secret key. The same RLS
boundary and service-level authorization apply. Database credentials remain
server-only; Supabase Auth and the frontend session flow are unchanged.

- RLS enabled with zero policies is deliberate, not an unfinished setup. Do not add permissive policies or point Flask at the publishable key: either reopens the back door.
- The secret key must only ever live in server environments (Render, local `backend/.env`), never in the frontend or in git.
