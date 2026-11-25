import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { Bet, Pick } from '#lib/types.ts';
import BetPicks from './BetPicks.svelte';

// The component reads the route's data from `page`; each test sets it here.
const page = vi.hoisted(() => ({ data: {} as Record<string, unknown> }));
vi.mock('$app/state', () => ({ page }));

const bet: Bet = {
	id: 'b1',
	pool_id: 'p1',
	statement: 'Who wins?',
	presentation: 'radio',
	winning_outcome_id: 'o1',
	options: [
		{ id: 'o1', label: 'Porto' },
		{ id: 'o2', label: 'Benfica' }
	],
	created_at: ''
};

function pick(id: string, name: string, outcome_id: string, bet_id = 'b1'): Pick {
	return { id, bet_id, user_id: id, user: { id, name }, outcome_id, created_at: '' };
}

const heading = { name: "Everyone's picks" };

describe('BetPicks', () => {
	beforeEach(() => {
		page.data = {
			pool: { status: 'LOCKED' },
			user: { id: 'a', name: 'Ana' },
			picks: [pick('a', 'Ana', 'o1'), pick('b', 'Bruno', 'o2'), pick('c', 'Carla', 'o1', 'b2')]
		};
	});

	it("lists this Bet's Picks and marks the winners", async () => {
		const screen = await render(BetPicks, { bet });
		const items = screen.getByRole('listitem');
		await expect.element(items.nth(0)).toHaveTextContent('Ana Porto Winner');
		await expect.element(items.nth(1)).toHaveTextContent('Bruno Benfica'); // exact text: no Winner tag
		await expect.element(items.nth(2)).not.toBeInTheDocument();
	});

	it('says so when nobody picked', async () => {
		page.data.picks = [];
		const screen = await render(BetPicks, { bet });
		await expect.element(screen.getByText('No picks for this bet.')).toBeVisible();
	});

	it.each([
		['the Pool is open', () => (page.data.pool = { status: 'OPEN' })],
		['nobody is logged in', () => (page.data.user = null)],
		['the Picks failed to load', () => (page.data.pickLoadError = 'down')]
	])('shows nothing when %s', async (_, setUp) => {
		setUp();
		const screen = await render(BetPicks, { bet });
		await expect.element(screen.getByRole('heading', heading)).not.toBeInTheDocument();
	});
});
