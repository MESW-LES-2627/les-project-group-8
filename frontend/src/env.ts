import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	API_URL: {
		schema: (value) => {
			if (!value) return undefined;
			try {
				return new URL(value).origin;
			} catch {
				throw new Error(`API_URL is not a valid URL: ${value}`);
			}
		}
	}
});
