import { SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL } from '$app/env/private';
import { createServerClient } from '@supabase/ssr';
import type { Handle } from '@sveltejs/kit/hooks';

export const handle: Handle = async ({ event, resolve }) => {
	// Read at request time (not module load) so `vite build` works without them.
	if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
		throw new Error(
			'SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are not configured. Set them in frontend/.env.'
		);
	}

	event.locals.supabase = createServerClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
		cookies: {
			getAll: () => event.cookies.getAll(),
			setAll: (cookiesToSet) => {
				for (const { name, value, options } of cookiesToSet) {
					// httpOnly: the browser never holds tokens; only this server reads them.
					event.cookies.set(name, value, { ...options, httpOnly: true, path: '/' });
				}
			}
		}
	});

	// Renews an expired access token from the refresh token (rewriting the cookies);
	// if that fails, the session is cleared and the request is logged out.
	// Only the access token is used, to call Flask, which verifies it (ADR 0001).
	const {
		data: { session }
	} = await event.locals.supabase.auth.getSession();
	event.locals.session = session;

	return resolve(event);
};
