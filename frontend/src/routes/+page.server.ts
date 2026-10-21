import { fail } from '@sveltejs/kit';
import { ApiError, createPool, listPools } from '#lib/server/api.ts';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = ({ fetch }) => {
	// Not awaited: the page renders immediately and streams the list in. This
	// matters on Render's free tier, where a cold start can take ~30s.
	// Resolve (never reject) so the real error message reaches the page.
	const pools = listPools(fetch).then(
		(items) => ({ ok: true as const, items }),
		(err) => ({
			ok: false as const,
			error: err instanceof ApiError ? err.message : 'Could not load pools.'
		})
	);
	return { pools };
};

export const actions: Actions = {
	create: async ({ request, fetch }) => {
		const form = await request.formData();
		const values = {
			name: String(form.get('name') ?? ''),
			statement: String(form.get('statement') ?? ''),
			deadline: String(form.get('deadline') ?? ''),
			optionA: String(form.get('optionA') ?? ''),
			optionB: String(form.get('optionB') ?? '')
		};

		const deadline = toUtcIso(values.deadline, Number(form.get('tzOffset') ?? 0));
		if (!deadline) {
			return fail(400, { values, error: 'Please pick a valid deadline.' });
		}

		try {
			const pool = await createPool(fetch, {
				name: values.name,
				statement: values.statement,
				deadline,
				options: [values.optionA, values.optionB]
			});
			return { created: pool.id };
		} catch (err) {
			if (err instanceof ApiError && err.status < 500) {
				return fail(err.status, { values, error: err.message });
			}
			console.error('Create pool failed', err);
			return fail(502, { values, error: 'Something went wrong on our side. Please try again.' });
		}
	}
};

/**
 * `<input type="datetime-local">` sends the user's local wall-clock time with
 * no zone ("2026-11-01T20:00"). The browser also sends its
 * `getTimezoneOffset()` in minutes, so the server (UTC on Cloudflare) can turn
 * that into a real instant.
 */
function toUtcIso(local: string, tzOffsetMinutes: number): string | null {
	if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(local)) return null;
	const asUtc = Date.parse(`${local}Z`);
	if (Number.isNaN(asUtc)) return null;
	const offset = Number.isFinite(tzOffsetMinutes) ? tzOffsetMinutes : 0;
	return new Date(asUtc + offset * 60_000).toISOString();
}
