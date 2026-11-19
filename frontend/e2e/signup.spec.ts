import { expect, test } from '@playwright/test';

test('a new visitor signs up and the header shows their name (US5)', async ({ page }) => {
	const id = crypto.randomUUID().slice(0, 8);
	const name = `E2E ${id}`;

	await page.goto('/signup');
	await page.getByLabel('Email').fill(`e2e-${id}@example.test`);
	await page.getByLabel('Password').fill('password123');
	await page.getByLabel('Name').fill(name);
	await page.getByRole('button', { name: 'Sign up' }).click();

	await expect(page).toHaveURL('/');
	const header = page.getByRole('banner');
	await expect(header.getByRole('button', { name: 'Log out' })).toBeVisible();
	// Exact, so the test fails if the header names anyone else.
	await expect(header.getByText(name, { exact: true })).toBeVisible();
});
