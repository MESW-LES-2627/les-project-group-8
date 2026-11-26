import { fail, redirect } from '@sveltejs/kit';
import { validateName } from '#lib/account.ts';
import { readField } from '#lib/form.ts';
import { loginPath } from '#lib/redirect.ts';
import { ApiError, renameCurrentUser } from '#lib/server/api.ts';
import { endSession } from '#lib/server/session.ts';

export function load({ locals, url }) {
	if (!locals.session) {
		redirect(303, loginPath(url));
	}
	return { saved: url.searchParams.has('saved') };
}

export const actions = {
	default: async ({ request, locals, cookies, url }) => {
		if (!locals.session) {
			redirect(303, loginPath(url));
		}

		const form = await request.formData();
		const { name, error } = validateName(readField(form, 'name'));
		const values = { name };
		if (error) {
			return fail(400, { error: 'Please fix the errors below.', fields: { name: error }, values });
		}

		try {
			await renameCurrentUser(name, locals.session.access_token);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			if (err instanceof ApiError && err.status === 403) {
				redirect(303, '/no-user');
			}
			if (err instanceof ApiError && err.status === 400) {
				return fail(400, { error: err.message, fields: { name: err.message }, values });
			}
			return fail(502, {
				error: err instanceof Error ? err.message : 'Could not save your name.',
				values
			});
		}

		redirect(303, '/account?saved=1');
	}
};
