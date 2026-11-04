import { error, fail, redirect } from '@sveltejs/kit';
import { loginPath } from '#lib/redirect.ts';
import { ApiError, getMyPick, getPool, savePick } from '#lib/server/api.ts';
import { clearSessionCookies, endSession } from '#lib/server/session.ts';

export async function load({ params, locals, cookies }) {
	let pool;
	try {
		pool = await getPool(params.id);
	} catch (err) {
		if (err instanceof ApiError && err.status === 404) {
			throw error(404, 'Pool not found');
		}
		return {
			pool: null,
			pick: null,
			loadError: err instanceof Error ? err.message : 'Could not load the pool.'
		};
	}

	let pick = null;
	if (locals.session) {
		try {
			pick = await getMyPick(pool.id, locals.session.access_token);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				// Flask refused the token: end this browser's session so the header agrees.
				clearSessionCookies(cookies);
				locals.session = null;
			} else if (!(err instanceof ApiError && err.status === 403)) {
				return {
					pool,
					pick: null,
					loadError: err instanceof Error ? err.message : 'Could not load your pick.'
				};
			}
		}
	}

	return { pool, pick, loadError: null };
}

export const actions = {
	default: async ({ params, request, locals, cookies, url }) => {
		// Picking needs a logged-in User: Flask makes the token's User the participant.
		if (!locals.session) redirect(303, loginPath(url));

		const form = await request.formData();
		const outcomeId = form.get('outcome_id');

		if (typeof outcomeId !== 'string' || !outcomeId) {
			return fail(400, { error: 'Choose an option before saving.' });
		}

		try {
			await savePick(params.id, outcomeId, locals.session.access_token);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			if (err instanceof ApiError && err.status === 403) {
				redirect(303, '/no-user');
			}
			if (err instanceof ApiError && (err.status === 400 || err.status === 404)) {
				return fail(400, { error: err.message });
			}
			return fail(502, {
				error: err instanceof Error ? err.message : 'Could not save your pick.'
			});
		}

		return { saved: true };
	}
};
