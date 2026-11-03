-- Flask is the only way into the app tables (ADR 0003). Run after 001_init.sql.
--
-- Row-level security is enabled with NO policies on purpose: Supabase's REST
-- API then refuses every direct read and write made with the publishable key
-- or an Account's token. Flask connects with the secret key, which bypasses
-- RLS. Do not add policies here: any policy reopens the back door.

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE pools ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE picks ENABLE ROW LEVEL SECURITY;
