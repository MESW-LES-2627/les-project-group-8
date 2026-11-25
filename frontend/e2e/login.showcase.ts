import { expect, test } from '@playwright/test';
import { waitForHydration } from './account.ts';

// Frozen, so a screen that shows a date or a countdown looks the same on every run.
test.beforeEach(async ({ page }) => {
	await page.clock.setFixedTime(new Date('2026-06-01T12:00:00Z'));
});

test('login', async ({ page }) => {
	await page.goto('/login');
	await waitForHydration(page);
	await expect.soft(page).toHaveScreenshot('login.png', { fullPage: true });
});
