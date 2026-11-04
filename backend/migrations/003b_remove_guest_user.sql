-- Every User belongs to an Account (#39). Run after 003a_create_user_on_signup.sql,
-- in the Supabase SQL editor.
--
-- WARNING: the Supabase project is shared by local, staging and production, so
-- this deletes the Iteration 0 Guest User and all its pools everywhere,
-- production included (accepted in #34). Their outcomes and picks go with them
-- (ON DELETE CASCADE).
--
-- One transaction: if any step fails, nothing is deleted. The foreign key fails
-- if some other User has no Account (e.g. one made through the removed
-- POST /api/users). List them with
--   SELECT u.id, u.name FROM public.users u
--   LEFT JOIN auth.users a ON a.id = u.id WHERE a.id IS NULL;
-- decide what to do with them and their pools, then run this again.

BEGIN;

DELETE FROM public.pools
WHERE creator_id = '00000000-0000-0000-0000-000000000001'
   OR decider_id = '00000000-0000-0000-0000-000000000001';

DELETE FROM public.users
WHERE id = '00000000-0000-0000-0000-000000000001';

ALTER TABLE public.users DROP COLUMN is_guest;

-- A User's id is its Account's id; deleting the Account deletes the User.
-- (Pools still reference their creator without a cascade, so an Account that
-- owns pools can only be deleted after those pools.)
ALTER TABLE public.users
  ADD CONSTRAINT users_id_fkey
  FOREIGN KEY (id) REFERENCES auth.users (id) ON DELETE CASCADE;

COMMIT;
