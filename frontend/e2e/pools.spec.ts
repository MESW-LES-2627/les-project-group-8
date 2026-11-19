import { expect, test, type Page } from '@playwright/test';
import { signUp, waitForHydration } from './account.ts';

const RADIO = { statement: 'Who wins the derby?', options: ['Home', 'Away', 'Draw'] };
const DROPDOWN = { statement: 'How many goals?', options: ['0–1', '2–3', '4 or more'] };

/** Creates a Pool through the form and returns its detail page's path. */
async function createPool(page: Page, description = ''): Promise<{ path: string; name: string }> {
	const name = `Pool ${crypto.randomUUID().slice(0, 8)}`;
	await page.goto('/pools/new');
	await waitForHydration(page);
	await page.getByLabel('Name').fill(name);
	await page.getByLabel('Description (optional)').fill(description);
	await page.getByLabel('Deadline').fill('2030-06-15T12:30');
	await page.getByRole('button', { name: 'Create pool' }).click();
	await page.waitForURL(/\/pools\/[^/?]+\?created/);
	return { path: new URL(page.url()).pathname, name };
}

async function addBet(
	page: Page,
	bet: { statement: string; options: string[] },
	presentation: 'Radio buttons' | 'Dropdown'
): Promise<void> {
	await page.getByLabel('Bet statement').fill(bet.statement);
	for (const [i, option] of bet.options.entries()) {
		if (i >= 2) await page.getByRole('button', { name: '+ Add option' }).click();
		await page.getByLabel(`Option ${i + 1}`, { exact: true }).fill(option);
	}
	await page.getByLabel(presentation).check();
	await page.getByRole('button', { name: 'Add bet' }).click();
	await expect(betCard(page, bet.statement)).toBeVisible();
}

const betCard = (page: Page, statement: string) =>
	page.getByRole('article').filter({ has: page.getByRole('heading', { name: statement }) });
const radio = (page: Page, label: string) => betCard(page, RADIO.statement).getByRole('radio', { name: label });
const dropdown = (page: Page) => betCard(page, DROPDOWN.statement).getByRole('combobox', { name: 'Your pick' });

/** Submits the Bet's pick form and waits until the saved Pick is shown. */
async function savePick(page: Page, statement: string, label: string): Promise<void> {
	const card = betCard(page, statement);
	await card.getByRole('button', { name: /^(Save|Change) pick$/ }).click();
	await expect(card.getByText(`Saved: ${label}`)).toBeVisible();
}

test('a new Pool is created empty and its page shows its name, description and deadline', async ({
	page
}) => {
	await signUp(page);
	const { name } = await createPool(page, 'Weekend football');

	await expect(page.getByRole('heading', { level: 1 })).toHaveText(name);
	await expect(page.getByText('Weekend football')).toBeVisible();
	// The page shows the deadline in UTC; the input took it in the server's local time.
	await expect(page.getByText(/^Deadline 15 Jun 2030, \d\d:30 UTC$/)).toBeVisible();
	await expect(page.getByText('No bets yet.')).toBeVisible();
});

test('the creator saves Picks on a radio and a dropdown Bet, then changes one after a reload', async ({
	page
}) => {
	await signUp(page);
	await createPool(page);
	await addBet(page, RADIO, 'Radio buttons');
	await addBet(page, DROPDOWN, 'Dropdown');

	await radio(page, 'Home').check();
	await savePick(page, RADIO.statement, 'Home');
	await dropdown(page).selectOption({ label: '2–3' });
	await savePick(page, DROPDOWN.statement, '2–3');

	await page.reload();
	await expect(radio(page, 'Home')).toBeChecked();
	await expect(dropdown(page).locator('option:checked')).toHaveText('2–3');

	await radio(page, 'Away').check();
	await savePick(page, RADIO.statement, 'Away');

	await page.reload();
	await expect(radio(page, 'Away')).toBeChecked();
	await expect(dropdown(page).locator('option:checked')).toHaveText('2–3');
});

test('before the deadline, another User sees neither the creator\'s Picks nor the authoring controls, and each keeps their own Pick (16.1–16.2)', async ({
	page,
	browser
}) => {
	await signUp(page);
	const { path } = await createPool(page);
	await addBet(page, RADIO, 'Radio buttons');
	await radio(page, 'Home').check();
	await savePick(page, RADIO.statement, 'Home');

	const context = await browser.newContext();
	const other = await context.newPage();
	const { name: otherName } = await signUp(other);
	await other.goto(path);
	await expect(betCard(other, RADIO.statement)).toBeVisible();
	await expect(radio(other, 'Home')).not.toBeChecked();
	await expect(other.getByText('Saved:')).toBeHidden();
	await expect(other.getByRole('heading', { name: 'Add a bet' })).toBeHidden();

	await radio(other, 'Draw').check();
	await savePick(other, RADIO.statement, 'Draw');
	await other.reload();
	await expect(radio(other, 'Draw')).toBeChecked();
	await expect(other.getByText('Saved: Draw')).toBeVisible();

	await page.reload();
	await expect(radio(page, 'Home')).toBeChecked();
	await expect(page.getByText('Saved: Home')).toBeVisible();
	// The leaderboard lists every User with a Pick; the Bet must not show whose Pick is whose.
	await expect(betCard(page, RADIO.statement).getByText(otherName)).toBeHidden();
	await context.close();
});

test('a dropdown Bet lists its Outcomes in order in a labelled dropdown with none selected (27.2)', async ({
	page
}) => {
	await signUp(page);
	await createPool(page);
	await addBet(page, DROPDOWN, 'Dropdown');

	await expect(dropdown(page).locator('option')).toHaveText(['Select an option', ...DROPDOWN.options]);
	await expect(dropdown(page)).toHaveValue('');
});
