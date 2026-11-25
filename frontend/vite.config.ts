import adapter from '@sveltejs/adapter-cloudflare';
import { sveltekit } from '@sveltejs/kit/vite';
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
		environment: 'node',
		// Unit tests only; Playwright specs (#33) live outside src/.
		include: ['src/**/*.test.ts'],
		// Only what unit tests own; routes, hooks, lib/server and components are e2e's.
		// Untested files listed here still count, so they show as gaps.
		coverage: {
			provider: 'v8',
			include: ['src/lib/*.ts', 'src/env.ts'],
			exclude: ['**/*.test.ts', 'src/lib/types.ts', 'src/lib/index.ts'],
			reportOnFailure: true, // so a red run still gets its summary and artifact
			reporter: ['text', ['text', { file: 'coverage.txt' }], 'html']
		}
	}
});
