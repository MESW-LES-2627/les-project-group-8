import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	API_URL: {
		description:
			'Base URL of the Flask backend, without /api (e.g. http://127.0.0.1:5000). Server-only: the browser never calls the backend directly.',
		schema: (value) => {
			// Optional so `vite build` works in CI without it; the Worker gets it
			// from wrangler `vars` at runtime. lib/server/api.ts fails loudly if unset.
			if (!value) return undefined;
			try {
				return new URL(value).origin;
			} catch {
				throw new Error(`API_URL is not a valid URL: ${value}`);
			}
		}
	}
});
