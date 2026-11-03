import { API_URL } from '$app/env/private';
import type { CreatePoolInput, Pool, UserSummary } from '#lib/types.ts';

const TIMEOUT_MS = 15_000;

export class ApiError extends Error {
	status: number;

	constructor(message: string, status: number) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
	}
}

function apiBase(): string {
	// Read at request time (not module load) so `vite build` works without API_URL.
	if (!API_URL) {
		throw new ApiError('API_URL is not configured. Set it in frontend/.env.', 0);
	}
	return `${API_URL.replace(/\/+$/, '')}/api`;
}

type RequestOptions = {
	method?: 'GET' | 'POST';
	/** Sent as JSON. */
	body?: unknown;
	/** The logged-in Account's Supabase access token; Flask verifies it (ADR 0001). */
	accessToken?: string;
};

async function request<T>(
	path: string,
	{ method = 'GET', body, accessToken }: RequestOptions = {}
): Promise<T> {
	const url = `${apiBase()}${path}`;
	const headers = new Headers({ accept: 'application/json' });
	if (body !== undefined) headers.set('content-type', 'application/json');
	if (accessToken) headers.set('authorization', `Bearer ${accessToken}`);

	let response: Response;
	try {
		response = await fetch(url, {
			method,
			headers,
			body: body === undefined ? undefined : JSON.stringify(body),
			signal: AbortSignal.timeout(TIMEOUT_MS)
		});
	} catch {
		throw new ApiError('Could not reach the backend. Is Flask running?', 0);
	}

	const text = await response.text();
	let data: unknown = null;
	if (text) {
		try {
			data = JSON.parse(text);
		} catch {
			data = null;
		}
	}

	if (!response.ok) {
		const message =
			data && typeof data === 'object' && 'error' in data
				? String((data as { error: unknown }).error)
				: `The backend returned ${response.status}.`;
		throw new ApiError(message, response.status);
	}

	return data as T;
}

export function listPools(): Promise<Pool[]> {
	return request<Pool[]>('/pools');
}

/** The User the access token belongs to. */
export function getCurrentUser(accessToken: string): Promise<UserSummary> {
	return request<UserSummary>('/me', { accessToken });
}

/** Flask makes the token's User the creator and decider. */
export function createPool(input: CreatePoolInput, accessToken: string): Promise<Pool> {
	return request<Pool>('/pools', { method: 'POST', body: input, accessToken });
}
