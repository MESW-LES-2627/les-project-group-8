import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { Bet, Pool } from '#lib/types.ts';
import PoolCard from './PoolCard.svelte';

const pool: Pool = {
	id: 'p1',
	name: 'Derby',
	description: 'Weekend games',
	deadline: '2030-01-01T12:00:00Z',
	status: 'OPEN',
	creator: { id: 'u1', name: 'Ana' },
	decider: { id: 'u1', name: 'Ana' },
	bets: [{ id: 'b1' } as Bet],
	created_at: ''
};

describe('PoolCard', () => {
	it('shows an open Pool with its description and one bet', async () => {
		const screen = await render(PoolCard, { pool });
		await expect.element(screen.getByText('Weekend games')).toBeVisible();
		await expect.element(screen.getByText('1 bet', { exact: true })).toBeVisible();
		await expect.element(screen.getByText('Picks open')).toBeVisible();
	});

	it('shows a locked Pool with no description and several bets', async () => {
		const screen = await render(PoolCard, {
			pool: { ...pool, description: '', status: 'LOCKED', bets: [...pool.bets, { id: 'b2' } as Bet] }
		});
		await expect.element(screen.getByText('Weekend games')).not.toBeInTheDocument();
		await expect.element(screen.getByText('2 bets')).toBeVisible();
		await expect.element(screen.getByText('Picks closed')).toBeVisible();
	});
});
