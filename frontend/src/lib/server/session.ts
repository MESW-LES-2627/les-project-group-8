import type { Cookies } from '@sveltejs/kit';

/** Logs this browser out: ends its Supabase session and clears the session cookies. */
export async function endSession(locals: App.Locals, cookies: Cookies): Promise<void> {
	// 'local' ends only this browser's session.
	const { error } = await locals.supabase.auth.signOut({ scope: 'local' });
	if (error) {
		// supabase-js keeps the cookies when it can't load the session (e.g. an expired
		// access token and Supabase unreachable for the renewal), so clear them here.
		for (const { name } of cookies.getAll()) {
			if (name.startsWith('sb-')) cookies.delete(name, { path: '/' });
		}
	}
	locals.session = null;
}
