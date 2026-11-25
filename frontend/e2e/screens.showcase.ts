import { expect, test, type Browser, type Page } from '@playwright/test';
import { signUp, waitForHydration } from './account.ts';
import { addBet, closePool, createPool, GOALS, pick, resolve, WINNER } from './pool.ts';

// Fixed names, fixed deadlines, a frozen clock and one zone: two runs of the same code give
// identical images. run.sh gives each run an empty database, so the fixed emails are free.
test.use({ timezoneId: 'UTC', locale: 'en-US' });
test.beforeEach(async ({ page }) => {
	await page.clock.setFixedTime(new Date('2026-06-01T12:00:00Z'));
});

const ANA = { email: 'ana@example.test', name: 'Ana Silva' };
const BEN = { email: 'ben@example.test', name: 'Ben Costa' };
const CLEO = { email: 'cleo@example.test', name: 'Cleo Dias' };

/** Signs up `account` in a browser of its own and picks on the Pool at `path`. */
async function pickAs(browser: Browser, account: typeof ANA, path: string, winner: string, goals: string): Promise<void> {
	const context = await browser.newContext();
	const page = await context.newPage();
	await signUp(page, account);
	await page.goto(path);
	await pick(page, winner, goals);
	await context.close();
}

async function screen(page: Page, path: string, name: string): Promise<void> {
	await page.goto(path);
	await waitForHydration(page);
	await expect.soft(page).toHaveScreenshot(name, { fullPage: true });
}

test('every screen', async ({ page, browser }) => {
	test.slow(); // three sign-ups and two Pools through the UI
	await screen(page, '/signup', 'signup.png');
	await signUp(page, ANA);
	await screen(page, '/pools/new', 'new-pool.png');

	const open = await createPool(page, 'Weekend derby', 'Saturday’s derby, before kick-off.');
	await addBet(page, WINNER);
	await addBet(page, GOALS);
	await pick(page, 'Home', '2–3');

	// After resolving: Ana 2–0, Ben 1–1, Cleo 0–2, so no tie leaves the order to chance.
	const closed = await createPool(page, 'Cup final', 'Last season’s final.');
	await addBet(page, WINNER);
	await addBet(page, GOALS);
	await pick(page, 'Home', '2–3');
	await pickAs(browser, BEN, closed, 'Home', '0–1');
	await pickAs(browser, CLEO, closed, 'Away', '4 or more');
	await closePool(closed); // a deadline cannot be set in the past through the UI
	await page.goto(closed);
	await waitForHydration(page);
	await resolve(page, WINNER.statement, 'Home');
	await resolve(page, GOALS.statement, '2–3');

	await screen(page, '/', 'pools.png');
	await screen(page, open, 'pool-open.png');
	await screen(page, closed, 'pool-closed.png');
	await expect.soft(page.getByRole('region', { name: 'Leaderboard' })).toHaveScreenshot('leaderboard.png');
});
