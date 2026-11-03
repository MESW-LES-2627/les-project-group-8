import { fail, redirect } from '@sveltejs/kit';
import { readField } from '#lib/form.ts';
import { sameSitePath } from '#lib/redirect.ts';
import { authFailureStatus, redirectIfLoggedIn } from '#lib/server/session.ts';

// One message for both wrong email and wrong password, so the page never reveals
// which emails have an Account.
const WRONG_CREDENTIALS = 'Incorrect email or password.';

export function load({ locals }) {
	redirectIfLoggedIn(locals);
}

export const actions = {
	default: async ({ request, locals, url }) => {
		const form = await request.formData();
		const email = readField(form, 'email').trim();
		const password = readField(form, 'password');
		// Never echo the password back into the form.
		const values = { email };

		if (!email || !password) {
			return fail(400, { error: 'Enter your email and password.', values });
		}

		const { error } = await locals.supabase.auth.signInWithPassword({ email, password });

		if (error) {
			if (error.code === 'invalid_credentials') {
				return fail(400, { error: WRONG_CREDENTIALS, values });
			}
			return fail(authFailureStatus(error), {
				error: error.message || 'Could not log you in.',
				values
			});
		}

		// The form posts to the page's own URL, so `redirectTo` is still in the query.
		redirect(303, sameSitePath(url.searchParams.get('redirectTo'), url));
	}
};
