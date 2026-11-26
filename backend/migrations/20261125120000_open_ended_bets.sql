-- #179 (US28): open-ended Bets collect free-text Picks.
-- Run after 20261104210948_pool_contains_bets.sql, together with the backend that reads answer_type.

BEGIN;

LOCK TABLE public.bets, public.picks IN ACCESS EXCLUSIVE MODE;

-- What kind of answer a Bet accepts; presentation stays a separate, choice-only concern.
-- Existing Bets keep their options and Picks as choice Bets.
ALTER TABLE public.bets
  ADD COLUMN answer_type TEXT NOT NULL DEFAULT 'choice'
    CONSTRAINT bets_answer_type_check CHECK (answer_type IN ('choice', 'text'));

-- A Pick stores either an Outcome (choice) or trimmed text (text), never both.
-- The composite foreign key to outcomes is not checked when outcome_id is NULL.
ALTER TABLE public.picks
  ALTER COLUMN outcome_id DROP NOT NULL,
  ADD COLUMN answer_text TEXT,
  ADD CONSTRAINT picks_one_answer_check
    CHECK ((outcome_id IS NULL) <> (answer_text IS NULL)),
  ADD CONSTRAINT picks_answer_text_check
    CHECK (answer_text IS NULL OR (answer_text = btrim(answer_text) AND char_length(answer_text) BETWEEN 1 AND 500));

NOTIFY pgrst, 'reload schema';

COMMIT;
