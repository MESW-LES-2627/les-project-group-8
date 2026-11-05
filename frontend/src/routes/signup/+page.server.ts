import { fail, redirect } from '@sveltejs/kit';
import { NAME_MAX, PASSWORD_MIN } from '#lib/account.ts';
import { readField } from '#lib/form.ts';
import { authFailureStatus, redirectIfLoggedIn } from '#lib/server/session.ts';

type FieldErrors = {
	email?: string;
	password?: string;
	name?: string;
};

type Values = { email: string; name: string };

function failure(status: number, error: string, values: Values, fields: FieldErrors = {}) {
	return fail(status, { error, fields, values });
}

export function load({ locals }) {
	redirectIfLoggedIn(locals);
}

export const actions = {
	default: async ({ request, locals }) => {
		const form = await request.formData();
		const email = readField(form, 'email').trim();
		const password = readField(form, 'password');
		const name = readField(form, 'name').trim();
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
				authFailureStatus(error),
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
