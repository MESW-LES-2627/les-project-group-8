import { redirect, type Cookies } from '@sveltejs/kit';

/** Logs this browser out: ends its Supabase session and clears the session cookies. */
export async function endSession(locals: App.Locals, cookies: Cookies): Promise<void> {
	// 'local' ends only this browser's session.
	const { error } = await locals.supabase.auth.signOut({ scope: 'local' });
	if (error) {
		// supabase-js keeps the cookies when it can't load the session (e.g. an expired
		// access token and Supabase unreachable for the renewal), so clear them here.
		clearSessionCookies(cookies);
	}
	locals.session = null;
}

/** Deletes the session cookies without telling Supabase, e.g. when they hold a forged token. */
export function clearSessionCookies(cookies: Cookies): void {
	for (const { name } of cookies.getAll()) {
		if (name.startsWith('sb-')) cookies.delete(name, { path: '/' });
	}
}

/** For /login and /signup: an already logged-in visitor goes home instead of starting a second session. */
export function redirectIfLoggedIn(locals: App.Locals): void {
	if (locals.session) redirect(303, '/');
}

/** A failed Supabase Auth call: the visitor's fault (400) or Supabase's (502). */
export function authFailureStatus(error: { status?: number }): 400 | 502 {
	return error.status && error.status < 500 ? 400 : 502;
}
