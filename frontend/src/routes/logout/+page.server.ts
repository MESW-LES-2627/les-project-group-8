import { redirect } from '@sveltejs/kit';
import { endSession } from '../../lib/server/session';

export function load() {
	// Logging out changes state, so it's a POST from the header's form; a GET just goes home.
	redirect(303, '/');
}

export const actions = {
	default: async ({ locals, cookies }) => {
		await endSession(locals, cookies);
		redirect(303, '/');
	}
};
