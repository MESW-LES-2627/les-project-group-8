import { describe, expect, it } from 'vitest';
import { render } from 'vitest-browser-svelte';
import Leaderboard from './Leaderboard.svelte';

const entries = [
	{ user: { id: 'u1', name: 'Ana' }, wins: 2, losses: 0, rank: 1 },
	{ user: { id: 'u2', name: 'Bruno' }, wins: 1, losses: 1, rank: 2 }
];

describe('Leaderboard', () => {
	it('says so when nobody has picked', async () => {
		const screen = await render(Leaderboard, { entries: [], currentUserId: null });
		await expect.element(screen.getByText('No picks in this pool yet.')).toBeVisible();
		await expect.element(screen.getByRole('table')).not.toBeInTheDocument();
	});

	it('lists each entry and marks the current User', async () => {
		const screen = await render(Leaderboard, { entries, currentUserId: 'u2' });
		await expect.element(screen.getByRole('rowheader', { name: 'Bruno (you)' })).toBeVisible();
		await expect.element(screen.getByRole('rowheader', { name: 'Ana', exact: true })).toBeVisible();
		await expect.element(screen.getByRole('row', { name: /Bruno/ })).toHaveClass('font-bold');
		await expect.element(screen.getByRole('row', { name: /Ana/ })).not.toHaveClass('font-bold');
	});
});
