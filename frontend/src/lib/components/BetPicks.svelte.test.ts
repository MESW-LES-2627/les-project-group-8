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
	answer_type: 'choice',
	presentation: 'radio',
	winning_outcome_id: 'o1',
	options: [
		{ id: 'o1', label: 'Porto' },
		{ id: 'o2', label: 'Benfica' }
	],
	created_at: ''
};

function pick(id: string, name: string, outcome_id: string, bet_id = 'b1'): Pick {
	return { id, bet_id, user_id: id, user: { id, name }, outcome_id, answer_text: null, created_at: '' };
}

const textBet: Bet = { ...bet, answer_type: 'text', options: [], winning_outcome_id: null };

function answer(id: string, name: string, answer_text: string): Pick {
	return { id, bet_id: 'b1', user_id: id, user: { id, name }, outcome_id: null, answer_text, created_at: '' };
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

	it("lists everyone's answers to a free-text Bet", async () => {
		page.data.picks = [answer('a', 'Ana', 'Ronaldo'), answer('b', 'Bruno', 'Messi')];
		const screen = await render(BetPicks, { bet: textBet });
		await expect.element(screen.getByRole('heading', { name: "Everyone's answers" })).toBeVisible();
		const items = screen.getByRole('listitem');
		await expect.element(items.nth(0)).toHaveTextContent('Ana Ronaldo');
		await expect.element(items.nth(1)).toHaveTextContent('Bruno Messi');
	});

	it('says so when nobody answered a free-text Bet', async () => {
		page.data.picks = [];
		const screen = await render(BetPicks, { bet: textBet });
		await expect.element(screen.getByText('No answers for this bet.')).toBeVisible();
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
