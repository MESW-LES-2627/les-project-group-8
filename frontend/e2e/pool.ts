import { expect, type Page } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';
import { waitForHydration } from './account.ts';

// Pools, Bets, Picks and results through the UI, for the showcase and story specs.

// playwright.config.ts refuses a non-local SUPABASE_URL (ADR 0005).
declare const process: { env: Record<string, string | undefined> }; // no @types/node here
const db = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_KEY!, {
	auth: { persistSession: false }
});

export type NewBet = { statement: string; options: string[]; presentation: 'Radio buttons' | 'Dropdown' };
export const WINNER: NewBet = { statement: 'Who wins the final?', options: ['Home', 'Away', 'Draw'], presentation: 'Radio buttons' };
export const GOALS: NewBet = { statement: 'How many goals?', options: ['0–1', '2–3', '4 or more'], presentation: 'Dropdown' };

/** Creates a Pool through the form and returns its detail page's path. */
export async function createPool(page: Page, name: string, description: string): Promise<string> {
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

export async function addBet(page: Page, bet: NewBet): Promise<void> {
	await page.getByLabel('Bet statement').fill(bet.statement);
	for (const [i, option] of bet.options.entries()) {
		if (i >= 2) await page.getByRole('button', { name: '+ Add option' }).click();
		await page.getByLabel(`Option ${i + 1}`, { exact: true }).fill(option);
	}
	await page.getByLabel(bet.presentation).check();
	await page.getByRole('button', { name: 'Add bet' }).click();
	await expect(betCard(page, bet.statement)).toBeVisible();
}

export const betCard = (page: Page, statement: string) =>
	page.getByRole('article').filter({ has: page.getByRole('heading', { name: statement }) });

/** Saves `label` as the Pick on the Bet with `statement`, on the Pool page the browser is on. */
export async function pickOutcome(page: Page, statement: string, label: string): Promise<void> {
	const card = betCard(page, statement);
	const dropdown = card.getByRole('combobox', { name: 'Your pick' });
	if (await dropdown.count()) await dropdown.selectOption({ label });
	else await card.getByRole('radio', { name: label }).check();
	await card.getByRole('button', { name: /Save pick|Change pick/ }).click();
	await expect(card.getByText(`Saved: ${label}`)).toBeVisible();
}

/** Picks `winner` on WINNER and `goals` on GOALS, on the Pool page the browser is on. */
export async function pick(page: Page, winner: string, goals: string): Promise<void> {
	await waitForHydration(page);
	await pickOutcome(page, WINNER.statement, winner);
	await pickOutcome(page, GOALS.statement, goals);
}

export async function resolve(page: Page, statement: string, winner: string): Promise<void> {
	const card = betCard(page, statement);
	await card.getByLabel('Winning outcome').selectOption({ label: winner });
	await card.getByRole('button', { name: 'Resolve bet' }).click();
	await expect(card.getByText(`Resolved — winning outcome: ${winner}`)).toBeVisible();
}

/** Moves the deadline of the Pool at `path` into the past: the UI only accepts future ones. */
export async function closePool(path: string): Promise<void> {
	const { error } = await db
		.from('pools')
		.update({ deadline: '2026-05-31T12:00:00Z' })
		.eq('id', path.split('/').pop()!);
	if (error) throw error;
}
