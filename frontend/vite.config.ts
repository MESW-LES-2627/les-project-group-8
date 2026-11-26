import adapter from '@sveltejs/adapter-cloudflare';
import { sveltekit } from '@sveltejs/kit/vite';
import { playwright } from '@vitest/browser-playwright';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},

			// Deploys to Cloudflare Workers (static assets + SSR).
			// See https://svelte.dev/docs/kit/adapter-cloudflare
			adapter: adapter()
		})
	],
	test: {
		// Playwright specs (#33) live outside src/.
		projects: [
			{
				extends: true,
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.test.ts'],
					exclude: ['src/**/*.svelte.test.ts']
				}
			},
			{
				extends: true,
				test: {
					name: 'client',
					include: ['src/**/*.svelte.test.ts'],
					browser: {
						enabled: true,
						provider: playwright(),
						headless: true,
						instances: [{ browser: 'chromium' }]
					}
				}
			}
		],
		// Only what unit and component tests own; routes, hooks and lib/server are e2e's.
		// Untested files listed here still count, so they show as gaps.
		coverage: {
			provider: 'v8',
			include: ['src/lib/*.ts', 'src/lib/components/*.svelte', 'src/env.ts'],
			exclude: ['**/*.test.ts', 'src/lib/types.ts', 'src/lib/index.ts'],
			reportOnFailure: true, // so a red run still gets its summary and artifact
			reporter: ['text', ['text', { file: 'coverage.txt' }], 'html']
		}
	}
});
