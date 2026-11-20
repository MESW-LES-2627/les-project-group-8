import { expect, test, type Page } from '@playwright/test';
import { editSession, logIn, signUp } from './account.ts';

const logOutButton = (page: Page) =>
	page.getByRole('banner').getByRole('button', { name: 'Log out' });

test('an existing Account logs in and stays logged in after a reload', async ({ page }) => {
	const { email, name } = await signUp(page);
	await logOutButton(page).click();
	await expect(logOutButton(page)).toBeHidden();

	await page.goto('/login');
	await logIn(page, email);

	await expect(page).toHaveURL('/');
	await expect(logOutButton(page)).toBeVisible();
	await page.reload();
	await expect(logOutButton(page)).toBeVisible();
	await expect(page.getByRole('banner').getByText(name, { exact: true })).toBeVisible();
});

test('logging out ends the session', async ({ page }) => {
	await signUp(page);
	await logOutButton(page).click();

	await expect(page).toHaveURL('/');
	await expect(logOutButton(page)).toBeHidden();
	await page.goto('/pools/new');
	await expect(page).toHaveURL(/\/login\?/);
});

test('an expired session that cannot be renewed is sent to login', async ({ page, context }) => {
	await signUp(page);
	await editSession(context, (session) => {
		session.expires_at = Math.floor(Date.now() / 1000) - 60;
		session.refresh_token = 'invalid';
	});

	await page.goto('/pools/new');
	await expect(page).toHaveURL(/\/login\?/);
});

test('a session with a forged access token is sent to login', async ({ page, context }) => {
	await signUp(page);
	await editSession(context, (session) => {
		const [header, payload, signature] = session.access_token.split('.');
		// Flip a character in the middle: the last one may carry only padding bits.
		const i = signature.length >> 1;
		const forged = signature.slice(0, i) + (signature[i] === 'A' ? 'B' : 'A') + signature.slice(i + 1);
		session.access_token = [header, payload, forged].join('.');
	});

	await page.goto('/pools/new');
	await expect(page).toHaveURL(/\/login\?/);
});

test('a logged-out visitor to the create-pool page logs in and comes back to it (2.11)', async ({
	page
}) => {
	const { email } = await signUp(page);
	await logOutButton(page).click();
	await expect(logOutButton(page)).toBeHidden();

	await page.goto('/pools/new');
	await expect(page).toHaveURL('/login?redirectTo=%2Fpools%2Fnew');
	await logIn(page, email);

	await expect(page).toHaveURL('/pools/new');
});
