import { expect, test, type Page } from '@playwright/test';
import { signUp, waitForHydration } from './account.ts';

/** Creates a Pool through the form and returns its detail page's path. */
async function createPool(page: Page): Promise<string> {
	const name = `Pool ${crypto.randomUUID().slice(0, 8)}`;
	await page.goto('/pools/new');
	await waitForHydration(page);
	await page.getByLabel('Name').fill(name);
	await page.getByLabel('Deadline').fill('2030-06-15T12:30');
	await page.getByRole('button', { name: 'Create pool' }).click();
	await page.waitForURL(/\/pools\/[^/?]+\?created/);
	return new URL(page.url()).pathname;
}

test('a User renames themselves and the header and pools show the new name (30.1, 30.4)', async ({
	page,
	browser
}) => {
	const { name } = await signUp(page);
	const poolPath = await createPool(page);

	// The name in the header opens the account page.
	const header = page.getByRole('banner');
	await header.getByRole('link', { name, exact: true }).click();
	await waitForHydration(page);
	await expect(page).toHaveURL('/account');

	const newName = `Renamed ${crypto.randomUUID().slice(0, 8)}`;
	await page.getByLabel('Name').fill(newName);
	await page.getByRole('button', { name: 'Save name' }).click();
	await expect(page).toHaveURL('/account?saved=1');
	await expect(page.getByRole('status')).toHaveText('Name updated.');

	await page.reload();
	await expect(header.getByText(newName, { exact: true })).toBeVisible();

	// Another visitor reloads the Pool where this User is the creator.
	const context = await browser.newContext();
	const visitor = await context.newPage();
	await visitor.goto(poolPath);
	await expect(visitor.getByText(`By ${newName}`, { exact: true })).toBeVisible();
	await context.close();
});

test('a blank name is rejected and the saved name stays (30.3)', async ({ page }) => {
	const { name } = await signUp(page);
	await page.goto('/account');
	await waitForHydration(page);

	const input = page.getByLabel('Name');
	await expect(input).toHaveValue(name);
	await input.fill('   ');
	await page.getByRole('button', { name: 'Save name' }).click();
	await expect(page.getByText('Name cannot be empty.')).toBeVisible();

	await page.reload();
	await expect(input).toHaveValue(name);
	await expect(page.getByRole('banner').getByText(name, { exact: true })).toBeVisible();
});

test('a signed-out visitor cannot open the account page (30.6)', async ({ page }) => {
	await page.goto('/account');
	await expect(page).toHaveURL('/login?redirectTo=%2Faccount');
});
