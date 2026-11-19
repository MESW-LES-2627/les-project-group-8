import type { BrowserContext, Page } from '@playwright/test';
import {
	combineChunks,
	createChunks,
	stringFromBase64URL,
	stringToBase64URL
} from '@supabase/ssr';
import type { Session } from '@supabase/supabase-js';

export const PASSWORD = 'password123';

/** Hydration resets fields filled before it, so a form filled too early posts nothing. */
export async function waitForHydration(page: Page): Promise<void> {
	await page.waitForLoadState('networkidle');
}

/** Signs up a fresh Account through the form; the browser ends up logged in on `/`. */
export async function signUp(page: Page): Promise<{ email: string; name: string }> {
	const id = crypto.randomUUID().slice(0, 8);
	const account = { email: `e2e-${id}@example.test`, name: `E2E ${id}` };

	await page.goto('/signup');
	await waitForHydration(page);
	await page.getByLabel('Email').fill(account.email);
	await page.getByLabel('Password').fill(PASSWORD);
	await page.getByLabel('Name').fill(account.name);
	await page.getByRole('button', { name: 'Sign up' }).click();
	await page.waitForURL('/');
	return account;
}

/** Fills and submits the login form on the page the browser is on. */
export async function logIn(page: Page, email: string): Promise<void> {
	await waitForHydration(page);
	await page.getByLabel('Email').fill(email);
	await page.getByLabel('Password').fill(PASSWORD);
	await page.getByRole('button', { name: 'Log in' }).click();
}

/**
 * Rewrites the Supabase session in the browser's cookies, as @supabase/ssr stores it:
 * `sb-<ref>-auth-token`, base64url with a `base64-` prefix, split into `.0`, `.1`… chunks.
 */
export async function editSession(
	context: BrowserContext,
	edit: (session: Session) => void
): Promise<void> {
	const cookies = (await context.cookies()).filter((c) => /^sb-.+-auth-token(\.\d+)?$/.test(c.name));
	const key = cookies[0]?.name.replace(/\.\d+$/, '');
	if (!key) throw new Error('No session cookie: is the browser logged in?');

	const stored = await combineChunks(key, (name) => cookies.find((c) => c.name === name)?.value);
	const session: Session = JSON.parse(stringFromBase64URL(stored!.slice('base64-'.length)));
	edit(session);

	const template = cookies[0];
	await context.clearCookies({ name: new RegExp(`^${key}`) });
	await context.addCookies(
		createChunks(key, 'base64-' + stringToBase64URL(JSON.stringify(session))).map((chunk) => ({
			...template,
			...chunk
		}))
	);
}
