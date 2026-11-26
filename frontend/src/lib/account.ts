// Account rules, shared by the actions' checks and the forms' minlength/maxlength.

/** Same as the `users_name_valid` CHECK in migration 003a, which is only a backstop. */
export const NAME_MAX = 80;
/** Supabase Auth's default minimum. */
export const PASSWORD_MIN = 6;

/**
 * Checks a display name after trimming it, the same rule the sign-up trigger and
 * `PATCH /api/me` save with. `name` is always the trimmed value, for redisplay.
 */
export function validateName(raw: string): { name: string; error?: string } {
	const name = raw.trim();
	if (!name) {
		return { name, error: 'Name cannot be empty.' };
	}
	if (name.length > NAME_MAX) {
		return { name, error: `Name must be at most ${NAME_MAX} characters.` };
	}
	return { name };
}
