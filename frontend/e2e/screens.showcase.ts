import { expect, test, type Browser, type Page } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';
import { signUp, waitForHydration } from './account.ts';

// Fixed names, fixed deadlines, a frozen clock and one zone: two runs of the same code give
// identical images. run.sh gives each run an empty database, so the fixed emails are free.
test.use({ timezoneId: 'UTC', locale: 'en-US' });
test.beforeEach(async ({ page }) => {
	await page.clock.setFixedTime(new Date('2026-06-01T12:00:00Z'));
});

// A deadline cannot be set in the past through the UI, so the closed Pool's is moved there
// once its Picks are in. playwright.config.ts refuses a non-local SUPABASE_URL (ADR 0005).
declare const process: { env: Record<string, string | undefined> }; // no @types/node here
const db = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!, {
	auth: { persistSession: false }
});

const ANA = { email: 'ana@example.test', name: 'Ana Silva' };
const BEN = { email: 'ben@example.test', name: 'Ben Costa' };
const CLEO = { email: 'cleo@example.test', name: 'Cleo Dias' };

type NewBet = { statement: string; options: string[]; presentation: 'Radio buttons' | 'Dropdown' };
const WINNER: NewBet = { statement: 'Who wins the final?', options: ['Home', 'Away', 'Draw'], presentation: 'Radio buttons' };
const GOALS: NewBet = { statement: 'How many goals?', options: ['0–1', '2–3', '4 or more'], presentation: 'Dropdown' };

/** Creates a Pool through the form and returns its detail page's path. */
async function createPool(page: Page, name: string, description: string): Promise<string> {
	await page.goto('/pools/new');
	await waitForHydration(page);
	await page.getByLabel('Name').fill(name);
	await page.getByLabel('Description (optional)').fill(description);
	// shortcut: the server judges deadlines by its real clock, so the open Pool closes in 2030; move it on before then.
	await page.getByLabel('Deadline').fill('2030-06-15T12:30');
	await page.getByRole('button', { name: 'Create pool' }).click();
	await page.waitForURL(/\/pools\/[^/?]+\?created/);
	return new URL(page.url()).pathname;
}

async function addBet(page: Page, bet: NewBet): Promise<void> {
	await page.getByLabel('Bet statement').fill(bet.statement);
	for (const [i, option] of bet.options.entries()) {
		if (i >= 2) await page.getByRole('button', { name: '+ Add option' }).click();
		await page.getByLabel(`Option ${i + 1}`, { exact: true }).fill(option);
	}
	await page.getByLabel(bet.presentation).check();
	await page.getByRole('button', { name: 'Add bet' }).click();
	await expect(betCard(page, bet.statement)).toBeVisible();
}

const betCard = (page: Page, statement: string) =>
	page.getByRole('article').filter({ has: page.getByRole('heading', { name: statement }) });

/** Picks `winner` on WINNER and `goals` on GOALS, on the Pool page the browser is on. */
async function pick(page: Page, winner: string, goals: string): Promise<void> {
	await waitForHydration(page);
	const winnerCard = betCard(page, WINNER.statement);
	await winnerCard.getByRole('radio', { name: winner }).check();
	await winnerCard.getByRole('button', { name: 'Save pick' }).click();
	await expect(winnerCard.getByText(`Saved: ${winner}`)).toBeVisible();
	const goalsCard = betCard(page, GOALS.statement);
	await goalsCard.getByRole('combobox', { name: 'Your pick' }).selectOption({ label: goals });
	await goalsCard.getByRole('button', { name: 'Save pick' }).click();
	await expect(goalsCard.getByText(`Saved: ${goals}`)).toBeVisible();
}

/** Signs up `account` in a browser of its own and picks on the Pool at `path`. */
async function pickAs(browser: Browser, account: typeof ANA, path: string, winner: string, goals: string): Promise<void> {
	const context = await browser.newContext();
	const page = await context.newPage();
	await signUp(page, account);
	await page.goto(path);
	await pick(page, winner, goals);
	await context.close();
}

async function resolve(page: Page, statement: string, winner: string): Promise<void> {
	const card = betCard(page, statement);
	await card.getByLabel('Winning outcome').selectOption({ label: winner });
	await card.getByRole('button', { name: 'Resolve bet' }).click();
	await expect(card.getByText(`Resolved — winning outcome: ${winner}`)).toBeVisible();
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
	const { error } = await db
		.from('pools')
		.update({ deadline: '2026-05-31T12:00:00Z' })
		.eq('id', closed.split('/').pop()!);
	if (error) throw error;
	await page.goto(closed);
	await waitForHydration(page);
	await resolve(page, WINNER.statement, 'Home');
	await resolve(page, GOALS.statement, '2–3');

	await screen(page, '/', 'pools.png');
	await screen(page, open, 'pool-open.png');
	await screen(page, closed, 'pool-closed.png');
	await expect.soft(page.getByRole('region', { name: 'Leaderboard' })).toHaveScreenshot('leaderboard.png');
});
