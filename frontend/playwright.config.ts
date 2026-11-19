import { defineConfig, devices } from '@playwright/test';

// e2e/run.sh starts a throwaway local Supabase and exports its URL and keys (ADR 0005).
// Without them, `vite preview` falls back to wrangler.jsonc's vars: the shared hosted project.
if (!process.env.SUPABASE_URL?.startsWith('http://127.0.0.1:')) {
	throw new Error('Run the e2e tests with `pnpm test:e2e`, which starts a local Supabase.');
}

// Not the dev ports (5001, 5173), so a running dev server is never reused.
const API_PORT = 5002;
const PORT = 4173;

export default defineConfig({
	testDir: 'e2e',
	forbidOnly: !!process.env.CI,
	reporter: process.env.CI ? [['github'], ['html', { open: 'never' }]] : 'list',
	use: {
		baseURL: `http://localhost:${PORT}`,
		trace: 'retain-on-failure'
	},
	projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
	webServer: [
		{
			command: `flask --app app run --port ${API_PORT}`,
			cwd: '../backend',
			url: `http://127.0.0.1:${API_PORT}/api/health`
		},
		{
			command: `pnpm build && pnpm preview --port ${PORT} --strictPort`,
			url: `http://localhost:${PORT}`,
			env: { API_URL: `http://127.0.0.1:${API_PORT}` },
			timeout: 120_000
		}
	]
});
