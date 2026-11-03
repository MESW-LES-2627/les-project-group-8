import { ApiError, getCurrentUser } from '#lib/server/api.ts';
import { clearSessionCookies } from '#lib/server/session.ts';
import type { UserSummary } from '#lib/types.ts';

export async function load({ locals, cookies }) {
	let user: UserSummary | null = null;

	if (locals.session) {
		try {
			user = await getCurrentUser(locals.session.access_token);
		} catch (error) {
			if (error instanceof ApiError && error.status === 401) {
				// Flask refused the token (the hook already checked its signature, so this is rare):
				// the visitor is logged out.
				clearSessionCookies(cookies);
				locals.session = null;
			}
			// Otherwise Flask is unreachable or the Account has no User (403): keep the session.
			// The pool list reports outages; /pools/new explains a missing User.
		}
	}

	// Separate from `user`: with a session but no User, /login and /signup redirect home,
	// so the header must still offer Log out.
	return { user, loggedIn: locals.session !== null };
}
