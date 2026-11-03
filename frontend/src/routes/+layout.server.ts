import { getMe } from '../lib/server/api';
import type { UserSummary } from '../lib/types';

export async function load({ locals }) {
	let user: UserSummary | null = null;

	if (locals.session) {
		try {
			user = await getMe(locals.session.access_token);
		} catch {
			// Flask refused the token (401/403) or is unreachable: show the page
			// as logged out rather than failing it. The pool list reports outages.
		}
	}

	// Separate from `user`: with a session but no User (Flask down or refusing the token),
	// /login and /signup redirect home, so the header must still offer Log out.
	return { user, loggedIn: locals.session !== null };
}
