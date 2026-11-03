import { fail, redirect } from '@sveltejs/kit';

// Same rules as the `users_name_valid` CHECK in migration 003a, which is only a backstop.
const NAME_MAX = 80;
// Supabase Auth's default minimum.
const PASSWORD_MIN = 6;

type FieldErrors = {
	email?: string;
	password?: string;
	name?: string;
};

type Values = { email: string; name: string };

function failure(status: number, error: string, values: Values, fields: FieldErrors = {}) {
	return fail(status, { error, fields, values });
}

function read(form: FormData, key: string): string {
	const value = form.get(key);
	return typeof value === 'string' ? value : '';
}

export function load({ locals }) {
	// Already logged in: don't start a second session.
	if (locals.session) redirect(303, '/');
}

export const actions = {
	default: async ({ request, locals }) => {
		const form = await request.formData();
		const email = read(form, 'email').trim();
		const password = read(form, 'password');
		const name = read(form, 'name').trim();
		// Never echo the password back into the form.
		const values: Values = { email, name };

		const fields: FieldErrors = {};
		if (!email) {
			fields.email = 'Email cannot be empty.';
		}
		if (password.length < PASSWORD_MIN) {
			fields.password = `Password must be at least ${PASSWORD_MIN} characters.`;
		}
		if (!name) {
			fields.name = 'Name cannot be empty.';
		} else if (name.length > NAME_MAX) {
			fields.name = `Name must be at most ${NAME_MAX} characters.`;
		}
		if (Object.keys(fields).length > 0) {
			return failure(400, 'Please fix the errors below.', values, fields);
		}

		// The `name` metadata becomes the User's name (trigger in migration 003a).
		const { data, error } = await locals.supabase.auth.signUp({
			email,
			password,
			options: { data: { name } }
		});

		if (error) {
			if (error.code === 'user_already_exists' || error.code === 'email_exists') {
				return failure(400, 'An account with this email already exists.', values);
			}
			if (error.code === 'weak_password') {
				return failure(400, error.message, values);
			}
			return failure(
				error.status && error.status < 500 ? 400 : 502,
				error.message || 'Could not create the account.',
				values
			);
		}

		if (!data.session) {
			// Supabase only skips the session when "Confirm email" is on (ADR 0002 turns it off).
			return failure(
				500,
				'Your account was created, but you could not be logged in. Please try logging in.',
				values
			);
		}

		redirect(303, '/');
	}
};
