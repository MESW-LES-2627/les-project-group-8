CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  is_guest BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE pools (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  statement TEXT NOT NULL,
  deadline TIMESTAMPTZ NOT NULL,
  creator_id UUID NOT NULL REFERENCES users(id),
  decider_id UUID NOT NULL REFERENCES users(id),
  winning_outcome_id UUID NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE outcomes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pool_id UUID NOT NULL REFERENCES pools(id) ON DELETE CASCADE,
  label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS picks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pool_id UUID NOT NULL REFERENCES pools(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  outcome_id UUID NOT NULL REFERENCES outcomes(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_pool_user UNIQUE (pool_id, user_id)
);

-- Pre-seed the mocked user for Iteration 0
INSERT INTO users (id, name, is_guest)
VALUES ('00000000-0000-0000-0000-000000000001', 'Guest User', true)
ON CONFLICT (id) DO NOTHING;
