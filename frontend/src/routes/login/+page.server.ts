import { fail, redirect } from '@sveltejs/kit';
import { sameSitePath } from '../../lib/redirect';

// One message for both wrong email and wrong password, so the page never reveals
// which emails have an Account.
const WRONG_CREDENTIALS = 'Incorrect email or password.';

function read(form: FormData, key: string): string {
	const value = form.get(key);
	return typeof value === 'string' ? value : '';
}

export function load({ locals }) {
	// Already logged in: don't start a second session.
	if (locals.session) redirect(303, '/');
}

export const actions = {
	default: async ({ request, locals, url }) => {
		const form = await request.formData();
		const email = read(form, 'email').trim();
		const password = read(form, 'password');
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
			return fail(error.status && error.status < 500 ? 400 : 502, {
				error: error.message || 'Could not log you in.',
				values
			});
		}

		// The form posts to the page's own URL, so `redirectTo` is still in the query.
		redirect(303, sameSitePath(url.searchParams.get('redirectTo'), url));
	}
};
