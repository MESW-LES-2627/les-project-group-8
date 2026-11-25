import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { Bet, Pick } from '#lib/types.ts';
import CorrectPickers from './CorrectPickers.svelte';

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

const heading = { name: 'Correct pickers — Porto' };

describe('CorrectPickers', () => {
	beforeEach(() => {
		page.data = {
			pool: { status: 'LOCKED' },
			user: { id: 'u1', name: 'Ana' },
			picks: [pick('a', 'Ana', 'o1'), pick('b', 'Bruno', 'o2'), pick('c', 'Carla', 'o1', 'b2')]
		};
	});

	it('lists only the Users who picked the winner of this Bet', async () => {
		const screen = await render(CorrectPickers, { bet });
		await expect.element(screen.getByRole('heading', heading)).toBeVisible();
		await expect.element(screen.getByRole('listitem')).toHaveTextContent('Ana');
	});

	it('says so when nobody picked the winner', async () => {
		page.data.picks = [pick('b', 'Bruno', 'o2')];
		const screen = await render(CorrectPickers, { bet });
		await expect.element(screen.getByText('Nobody picked the winner.')).toBeVisible();
	});

	it.each([
		['the Bet has no winner', () => ({ bet: { ...bet, winning_outcome_id: null } })],
		['the Pool is open', () => ((page.data.pool = { status: 'OPEN' }), { bet })],
		['nobody is logged in', () => ((page.data.user = null), { bet })],
		['the Picks failed to load', () => ((page.data.pickLoadError = 'down'), { bet })]
	])('shows nothing when %s', async (_, setUp) => {
		const screen = await render(CorrectPickers, setUp());
		await expect.element(screen.getByRole('heading', heading)).not.toBeInTheDocument();
	});
});
