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
	},
	SUPABASE_URL: {
		description:
			'Supabase project URL (e.g. https://<ref>.supabase.co). Server-only: sessions live in httpOnly cookies, so the browser never talks to Supabase.',
		schema: (value) => {
			// Optional for the same reason as API_URL; hooks.server.ts fails loudly if unset.
			if (!value) return undefined;
			try {
				return new URL(value).origin;
			} catch {
				throw new Error(`SUPABASE_URL is not a valid URL: ${value}`);
			}
		}
	},
	SUPABASE_PUBLISHABLE_KEY: {
		description:
			'Supabase publishable key (sb_publishable_…). Public by design, but only the SvelteKit server uses it. Never the secret key.',
		schema: (value) => value || undefined
	}
});
