import { redirect } from '@sveltejs/kit';

export function load() {
	// Logging out changes state, so it's a POST from the header's form; a GET just goes home.
	redirect(303, '/');
}

export const actions = {
	default: async ({ locals, cookies }) => {
		// 'local' ends only this browser's session.
		const { error } = await locals.supabase.auth.signOut({ scope: 'local' });
		if (error) {
			// supabase-js keeps the cookies when it can't load the session (e.g. an expired
			// access token and Supabase unreachable for the renewal), so clear them here.
			for (const { name } of cookies.getAll()) {
				if (name.startsWith('sb-')) cookies.delete(name, { path: '/' });
			}
		}
		redirect(303, '/');
	}
};
