-- Unused alternative: atomic pool creation + deterministic outcome order.
-- The current backend uses direct table requests and does not call this function.
-- If adopting this alternative later, run after 001_init.sql.

ALTER TABLE outcomes ADD COLUMN IF NOT EXISTS position SMALLINT NOT NULL DEFAULT 0;

-- Inserts a pool and its outcomes in a single transaction and returns the
-- new pool id. A future adapter could call supabase.rpc('create_pool', ...).
-- Current business-rule validation lives in pools/service.py.
CREATE OR REPLACE FUNCTION create_pool(
  p_name TEXT,
  p_statement TEXT,
  p_deadline TIMESTAMPTZ,
  p_creator_id UUID,
  p_decider_id UUID,
  p_options TEXT[]
) RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
  v_pool_id UUID;
BEGIN
  INSERT INTO pools (name, statement, deadline, creator_id, decider_id)
  VALUES (p_name, p_statement, p_deadline, p_creator_id, p_decider_id)
  RETURNING id INTO v_pool_id;

  INSERT INTO outcomes (pool_id, label, position)
  SELECT v_pool_id, opt.label, opt.ord - 1
  FROM unnest(p_options) WITH ORDINALITY AS opt(label, ord);

  RETURN v_pool_id;
END;
$$;

-- Make PostgREST pick up the new column and function immediately.
NOTIFY pgrst, 'reload schema';
