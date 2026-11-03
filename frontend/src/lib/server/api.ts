import { API_URL } from '$app/env/private';
import type { CreatePoolInput, Pool, UserSummary } from '../types';

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

/** `accessToken` is the logged-in Account's Supabase access token; Flask verifies it (ADR 0001). */
async function request<T>(path: string, init?: RequestInit, accessToken?: string): Promise<T> {
	const url = `${apiBase()}${path}`;
	const headers = new Headers(init?.headers);
	headers.set('accept', 'application/json');
	if (init?.body) headers.set('content-type', 'application/json');
	if (accessToken) headers.set('authorization', `Bearer ${accessToken}`);

	let response: Response;
	try {
		response = await fetch(url, {
			...init,
			headers,
			signal: AbortSignal.timeout(TIMEOUT_MS)
		});
	} catch {
		throw new ApiError('Could not reach the backend. Is Flask running?', 0);
	}

	const text = await response.text();
	let body: unknown = null;
	if (text) {
		try {
			body = JSON.parse(text);
		} catch {
			body = null;
		}
	}

	if (!response.ok) {
		const message =
			body && typeof body === 'object' && 'error' in body
				? String((body as { error: unknown }).error)
				: `The backend returned ${response.status}.`;
		throw new ApiError(message, response.status);
	}

	return body as T;
}

export function listPools(): Promise<Pool[]> {
	return request<Pool[]>('/pools');
}

/** The User the access token belongs to. */
export function getMe(accessToken: string): Promise<UserSummary> {
	return request<UserSummary>('/me', undefined, accessToken);
}

/** Flask makes the token's User the creator and decider. */
export function createPool(input: CreatePoolInput, accessToken: string): Promise<Pool> {
	return request<Pool>(
		'/pools',
		{
			method: 'POST',
			body: JSON.stringify(input)
		},
		accessToken
	);
}
