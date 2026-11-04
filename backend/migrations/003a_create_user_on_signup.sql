-- Every new Account gets its User (#37). Run after 001_init.sql, in the
-- Supabase SQL editor.
--
-- An Account lives in Supabase Auth (auth.users); its User is our row in
-- public.users and shares its id. Nothing in the app creates Users directly:
-- this trigger does, named from the Account's `name` metadata (sent by the
-- sign-up form), falling back to the part of the email before `@`.

-- Backstop for the sign-up form's check: trimmed, non-empty, at most 80 characters.
ALTER TABLE users
  ADD CONSTRAINT users_name_valid
  CHECK (name = btrim(name, E' \t\r\n') AND char_length(name) BETWEEN 1 AND 80);

-- New Users are real people, not the Iteration 0 guest. The column itself is
-- dropped along with the Guest User later, so the trigger doesn't mention it.
ALTER TABLE users ALTER COLUMN is_guest SET DEFAULT false;

-- SECURITY DEFINER: runs as the table owner, since the role inserting into
-- auth.users (Supabase Auth) has no rights on public.users. The empty
-- search_path makes every name below schema-qualified on purpose.
CREATE OR REPLACE FUNCTION public.create_user_for_account()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
  INSERT INTO public.users (id, name)
  VALUES (
    NEW.id,
    COALESCE(
      NULLIF(btrim(NEW.raw_user_meta_data ->> 'name', E' \t\r\n'), ''),
      split_part(NEW.email, '@', 1)
    )
  );
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_account_created ON auth.users;
CREATE TRIGGER on_account_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.create_user_for_account();
