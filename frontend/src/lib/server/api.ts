import { API_URL } from '$app/env/private';
import type { CreatePoolRequest, Pool } from '#lib/types.ts';

type Fetch = typeof fetch;

/** The backend answered with a non-2xx status. `message` is safe to show users. */
export class ApiError extends Error {
	status: number;

	constructor(status: number, message: string) {
		super(message);
		this.status = status;
	}
}

async function request<T>(fetch: Fetch, path: string, init?: RequestInit): Promise<T> {
	if (!API_URL) {
		throw new Error('API_URL is not set. Copy frontend/.env.example to frontend/.env.');
	}

	let response: Response;
	try {
		response = await fetch(`${API_URL}/api${path}`, {
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

export function listPools(fetch: Fetch): Promise<Pool[]> {
	return request(fetch, '/pools');
}

export function createPool(fetch: Fetch, payload: CreatePoolRequest): Promise<Pool> {
	return request(fetch, '/pools', { method: 'POST', body: JSON.stringify(payload) });
}
