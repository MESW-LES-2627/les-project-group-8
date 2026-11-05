-- #29: a Pool is a container; each Bet has its own options and Picks.
-- please review this file as well.
-- Run after 003/003a/003b and 004_multiple_choice.sql.

BEGIN;

LOCK TABLE public.pools, public.outcomes, public.picks IN ACCESS EXCLUSIVE MODE;

ALTER TABLE public.pools
  ADD COLUMN description TEXT NOT NULL DEFAULT '';

CREATE TABLE public.bets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pool_id UUID NOT NULL REFERENCES public.pools(id) ON DELETE CASCADE,
  statement TEXT NOT NULL,
  presentation TEXT NOT NULL DEFAULT 'radio'
    CHECK (presentation IN ('radio', 'dropdown')),
  winning_outcome_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Keep ADR 0003: only Flask's secret-key connection can access the app tables.
ALTER TABLE public.bets ENABLE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.bets TO service_role;

-- Each existing question becomes the first Bet of its Pool. Reusing its id
-- preserves the existing option/Pick references; new Bets get independent UUIDs.
INSERT INTO public.bets (id, pool_id, statement, presentation, winning_outcome_id, created_at)
SELECT id, id, statement, presentation, winning_outcome_id, created_at
FROM public.pools;

ALTER TABLE public.outcomes DROP CONSTRAINT outcomes_pool_id_fkey;
ALTER TABLE public.outcomes RENAME COLUMN pool_id TO bet_id;
ALTER TABLE public.outcomes
  ADD CONSTRAINT outcomes_bet_id_fkey
    FOREIGN KEY (bet_id) REFERENCES public.bets(id) ON DELETE CASCADE,
  ADD CONSTRAINT outcomes_id_bet_id_key UNIQUE (id, bet_id);
ALTER INDEX public.idx_outcomes_pool_position RENAME TO idx_outcomes_bet_position;

ALTER TABLE public.picks DROP CONSTRAINT picks_pool_id_fkey;
ALTER TABLE public.picks RENAME COLUMN pool_id TO bet_id;
ALTER TABLE public.picks RENAME CONSTRAINT uq_pool_user TO uq_bet_user;
ALTER TABLE public.picks
  ADD CONSTRAINT picks_bet_id_fkey
    FOREIGN KEY (bet_id) REFERENCES public.bets(id) ON DELETE CASCADE,
  ADD CONSTRAINT picks_outcome_bet_fkey
    FOREIGN KEY (outcome_id, bet_id) REFERENCES public.outcomes(id, bet_id) ON DELETE CASCADE,
  DROP CONSTRAINT picks_outcome_id_fkey;

-- The stored winner must also be an option of that same Bet.
ALTER TABLE public.bets
  ADD CONSTRAINT bets_winning_outcome_fkey
    FOREIGN KEY (winning_outcome_id, id) REFERENCES public.outcomes(id, bet_id);
CREATE INDEX bets_pool_id_idx ON public.bets(pool_id);

-- Pool keeps its identity, name, creator, decider, creation date and shared deadline.
ALTER TABLE public.pools
  DROP COLUMN statement,
  DROP COLUMN presentation,
  DROP COLUMN winning_outcome_id;

-- 002 was an unused alternative tied to the old schema; it may not be installed.
DROP FUNCTION IF EXISTS public.create_pool(TEXT, TEXT, TIMESTAMPTZ, UUID, UUID, TEXT[]);

NOTIFY pgrst, 'reload schema';

COMMIT;
