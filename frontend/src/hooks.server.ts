import { SUPABASE_PUBLISHABLE_KEY, SUPABASE_URL } from '$app/env/private';
import { createServerClient } from '@supabase/ssr';
import { isAuthRetryableFetchError } from '@supabase/supabase-js';
import type { Handle } from '@sveltejs/kit/hooks';
import { clearSessionCookies } from '#lib/server/session.ts';

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
			setAll: (cookiesToSet, headers) => {
				for (const { name, value, options } of cookiesToSet) {
					// httpOnly: the browser never holds tokens; only this server reads them.
					event.cookies.set(name, value, { ...options, httpOnly: true, path: '/' });
				}
				// No-store cache headers, so a CDN never serves one person's session cookies to another.
				event.setHeaders(headers);
			}
		}
	});

	// Renews an expired access token from the refresh token (rewriting the cookies);
	// if that fails, the session is cleared and the request is logged out.
	const {
		data: { session }
	} = await event.locals.supabase.auth.getSession();
	event.locals.session = session;

	// getSession() trusts whatever the cookie holds, so check the access token's signature
	// against Supabase's public keys (cached), as Flask does (ADR 0001). A tampered or
	// forged token logs the request out; Supabase being unreachable does not.
	if (session) {
		const { error } = await event.locals.supabase.auth.getClaims(session.access_token);
		if (error && !isAuthRetryableFetchError(error)) {
			clearSessionCookies(event.cookies);
			event.locals.session = null;
		}
	}

	return resolve(event);
};
