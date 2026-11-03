import { redirect } from '@sveltejs/kit';

export function load() {
	// Logging out changes state, so it's a POST from the header's form; a GET just goes home.
	redirect(303, '/');
}

export const actions = {
	default: async ({ locals }) => {
		// 'local' ends only this browser's session. supabase-js clears the session
		// cookies even when Supabase can't be reached to revoke the refresh token.
		await locals.supabase.auth.signOut({ scope: 'local' });
		redirect(303, '/');
	}
};
