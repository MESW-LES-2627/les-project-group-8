// Sign-up rules, shared by the action's checks and the form's minlength/maxlength.

/** Same as the `users_name_valid` CHECK in migration 003a, which is only a backstop. */
export const NAME_MAX = 80;
/** Supabase Auth's default minimum. */
export const PASSWORD_MIN = 6;
