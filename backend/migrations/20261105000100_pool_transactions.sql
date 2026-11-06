-- #31: one internal initial round; questions use the existing Bet model.
-- Run after 20261104210948_pool_contains_bets.sql. No round-management API.
BEGIN;

CREATE TABLE public.rounds (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pool_id UUID NOT NULL UNIQUE REFERENCES public.pools(id) ON DELETE CASCADE,
  deadline TIMESTAMPTZ NOT NULL,
  UNIQUE (id, pool_id)
);
ALTER TABLE public.rounds ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.rounds TO service_role;

INSERT INTO public.rounds (pool_id, deadline) SELECT id, deadline FROM public.pools;
ALTER TABLE public.bets ADD COLUMN round_id UUID;
UPDATE public.bets b SET round_id = r.id FROM public.rounds r WHERE r.pool_id = b.pool_id;
ALTER TABLE public.bets ALTER COLUMN round_id SET NOT NULL;
ALTER TABLE public.bets ADD CONSTRAINT bets_round_pool_fkey
  FOREIGN KEY (round_id, pool_id) REFERENCES public.rounds(id, pool_id) ON DELETE CASCADE;

COMMIT;
