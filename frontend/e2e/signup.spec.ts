import { expect, test } from '@playwright/test';
import { signUp } from './account.ts';

test('a new visitor signs up and the header shows their name (US5)', async ({ page }) => {
	const { name } = await signUp(page);

	await expect(page).toHaveURL('/');
	const header = page.getByRole('banner');
	await expect(header.getByRole('button', { name: 'Log out' })).toBeVisible();
	// Exact, so the test fails if the header names anyone else.
	await expect(header.getByText(name, { exact: true })).toBeVisible();
});
