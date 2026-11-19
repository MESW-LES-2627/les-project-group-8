#!/usr/bin/env bash
# Runs the Playwright specs against a throwaway local Supabase (ADR 0005): a fresh
# stack, every migration in backend/migrations/ applied in sorted order, and the
# stack removed on exit. Needs Docker and the Supabase CLI. Extra arguments go to
# `playwright test`.
set -euo pipefail
export LC_ALL=C # sorts 003_ before 003a_, the order the hosted project was migrated in
cd "$(dirname "$0")/../.."

# The hosted project signs with ES256, so the local one does too (ADR 0001).
keys=supabase/signing_keys.json
if [ ! -s "$keys" ]; then
	echo '[]' > "$keys"
	supabase gen signing-key --algorithm ES256 --append < /dev/null
fi

# A stack left over from a killed run would already hold the migrations.
supabase stop --no-backup > /dev/null 2>&1 || true
trap 'supabase stop --no-backup > /dev/null' EXIT
supabase start

# psql inside the database container, so the host needs no Postgres client.
# The container name comes from project_id in supabase/config.toml.
for migration in backend/migrations/*.sql; do
	echo "Applying $migration"
	docker exec -i supabase_db_les-project-group-8 \
		psql -q -U postgres -d postgres -v ON_ERROR_STOP=1 < "$migration"
done

# Prefixed, because the CLI's API_URL is Supabase's while the frontend's is Flask's.
eval "$(supabase status -o env | sed 's/^/LOCAL_/')"
export SUPABASE_URL=$LOCAL_API_URL
export SUPABASE_PUBLISHABLE_KEY=$LOCAL_PUBLISHABLE_KEY
export SUPABASE_KEY=$LOCAL_SECRET_KEY # Flask's

# Playwright starts Flask with `flask`: use the backend's venv when there is one.
if [ -d backend/.venv ]; then
	export PATH="$PWD/backend/.venv/bin:$PATH"
fi

cd frontend
pnpm exec playwright test "$@"
