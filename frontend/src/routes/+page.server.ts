import { fail } from '@sveltejs/kit';
import { API_URL } from '$app/env/private';
import type { Actions, PageServerLoad } from './$types';

export type PoolStatus = 'OPEN' | 'LOCKED' | 'RESOLVED';

export interface UserSummary {
	id: string;
	name: string;
}

export interface Outcome {
	id: string;
	label: string;
}

export interface Pool {
	id: string;
	name: string;
	statement: string;
	deadline: string;
	status: PoolStatus;
	creator: UserSummary;
	decider: UserSummary;
	options: Outcome[];
	winning_outcome_id: string | null;
}

export interface CreatePoolRequest {
	name: string;
	statement: string;
	deadline: string;
	options: [string, string];
}

class ApiError extends Error {
	status: number;

	constructor(status: number, message: string) {
		super(message);
		this.status = status;
	}
}

async function apiRequest<T>(fetchFn: typeof fetch, path: string, init?: RequestInit): Promise<T> {
	if (!API_URL) {
		throw new Error('API_URL is not set. Copy frontend/.env.example to frontend/.env.');
	}

	let response: Response;
	try {
		response = await fetchFn(`${API_URL}/api${path}`, {
			...init,
			headers: { 'content-type': 'application/json', ...init?.headers }
		});
	} catch (err) {
		console.error('Backend unreachable', err);
		throw new ApiError(503, 'The server is unreachable. Please try again in a moment.');
	}

	const body = await response.json().catch(() => null);
	if (!response.ok) {
		throw new ApiError(response.status, body?.error ?? `Request failed (${response.status}).`);
	}
	return body as T;
}

export const load: PageServerLoad = ({ fetch }) => {
	// Not awaited: the page renders immediately and streams the list in.
	const pools = apiRequest<Pool[]>(fetch, '/pools').then(
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
			const pool = await apiRequest<{ id?: string; pool_id?: string }>(
				fetch,
				'/pools',
				{
					method: 'POST',
					body: JSON.stringify({
						name: values.name,
						statement: values.statement,
						deadline,
						options: [values.optionA, values.optionB]
					})
				}
			);
			return { created: pool.id ?? pool.pool_id };
		} catch (err) {
			if (err instanceof ApiError && err.status < 500) {
				return fail(err.status, { values, error: err.message });
			}
			console.error('Create pool failed', err);
			return fail(502, { values, error: 'Something went wrong on our side. Please try again.' });
		}
	}
};

function toUtcIso(local: string, tzOffsetMinutes: number): string | null {
	if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(local)) return null;
	const asUtc = Date.parse(`${local}Z`);
	if (Number.isNaN(asUtc)) return null;
	const offset = Number.isFinite(tzOffsetMinutes) ? tzOffsetMinutes : 0;
	return new Date(asUtc + offset * 60_000).toISOString();
}
