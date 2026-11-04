-- Multiple-choice questions: ordered options and a presentation choice.
-- Run after 001_init.sql. Safe to run even if 002_create_pool_fn.sql was applied.

ALTER TABLE pools
  ADD COLUMN IF NOT EXISTS presentation TEXT NOT NULL DEFAULT 'radio'
  CONSTRAINT pools_presentation_check CHECK (presentation IN ('radio', 'dropdown'));

ALTER TABLE outcomes
  ADD COLUMN IF NOT EXISTS position SMALLINT NOT NULL DEFAULT 0;

-- Existing outcomes were created without an explicit position. Number them
-- deterministically so reads have a stable order from now on.
WITH ordered AS (
  SELECT id, row_number() OVER (PARTITION BY pool_id ORDER BY id) - 1 AS position
  FROM outcomes
)
UPDATE outcomes
SET position = ordered.position
FROM ordered
WHERE outcomes.id = ordered.id;

CREATE INDEX IF NOT EXISTS idx_outcomes_pool_position ON outcomes (pool_id, position);

-- Make PostgREST pick up the new column immediately.
NOTIFY pgrst, 'reload schema';
