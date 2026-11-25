import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { Bet } from '#lib/types.ts';
import ResolveControl from './ResolveControl.svelte';
import { finishSubmit, invalidateAll } from './form-actions.mock.ts';

// The component reads the route's data and action result from `page`; each test sets them here.
const page = vi.hoisted(() => ({
	data: {} as Record<string, unknown>,
	form: null as Record<string, unknown> | null
}));
vi.mock('$app/state', () => ({ page }));
vi.mock('$app/forms', () => import('./form-actions.mock.ts'));
vi.mock('$app/navigation', () => import('./form-actions.mock.ts'));

const bet: Bet = {
	id: 'b1',
	pool_id: 'p1',
	statement: 'Who wins?',
	presentation: 'radio',
	winning_outcome_id: null,
	options: [
		{ id: 'o1', label: 'Porto' },
		{ id: 'o2', label: 'Benfica' }
	],
	created_at: ''
};

const decider = { id: 'u1', name: 'Ana' };

describe('ResolveControl', () => {
	beforeEach(() => {
		page.data = { user: decider, pool: { status: 'LOCKED', decider } };
		page.form = null;
		invalidateAll.mockClear();
	});

	it('shows the winning Outcome once the Bet is resolved', async () => {
		const screen = await render(ResolveControl, { bet: { ...bet, winning_outcome_id: 'o2' } });
		await expect.element(screen.getByRole('status')).toHaveTextContent('Resolved — winning outcome: Benfica');
		await expect.element(screen.getByRole('button', { name: 'Resolve bet' })).not.toBeInTheDocument();
	});

	it('lets the Decider pick the winner of a locked Pool', async () => {
		const screen = await render(ResolveControl, { bet });
		const select = screen.getByRole('combobox', { name: 'Winning outcome' });
		await expect.element(select).toHaveValue('');
		await expect.element(screen.getByRole('button', { name: 'Resolve bet' })).toBeEnabled();
		await select.selectOptions('Porto');
		await expect.element(select).toHaveValue('o1');
	});

	it.each([
		['reloads the page after a failed resolve', 'failure', 1],
		['keeps the page after a successful resolve', 'success', 0]
	] as const)('disables the button while resolving and %s', async (_, type, reloads) => {
		const screen = await render(ResolveControl, { bet });
		await screen.getByRole('combobox', { name: 'Winning outcome' }).selectOptions('Porto');
		await screen.getByRole('button', { name: 'Resolve bet' }).click();
		await expect.element(screen.getByRole('button', { name: 'Resolving…' })).toBeDisabled();
		await finishSubmit(type);
		await expect.element(screen.getByRole('button', { name: 'Resolve bet' })).toBeEnabled();
		expect(invalidateAll).toHaveBeenCalledTimes(reloads);
	});

	it('keeps the chosen Outcome and shows the error after a failed resolve', async () => {
		page.form = { action: 'resolve', betId: 'b1', error: 'Try again.', winningOutcomeId: 'o2' };
		const screen = await render(ResolveControl, { bet });
		await expect.element(screen.getByRole('alert')).toHaveTextContent('Try again.');
		await expect.element(screen.getByRole('combobox', { name: 'Winning outcome' })).toHaveValue('o2');
	});

	it("ignores another Bet's resolve result", async () => {
		page.form = { action: 'resolve', betId: 'b2', error: 'Try again.' };
		const screen = await render(ResolveControl, { bet });
		await expect.element(screen.getByRole('alert')).not.toBeInTheDocument();
	});

	it.each([
		['the User is not the Decider', () => (page.data.user = { id: 'u2', name: 'Bruno' })],
		['nobody is logged in', () => (page.data.user = null)],
		['the Pool is still open', () => (page.data.pool = { status: 'OPEN', decider })]
	])('shows no form when %s', async (_, setUp) => {
		setUp();
		const screen = await render(ResolveControl, { bet });
		await expect.element(screen.getByRole('button', { name: 'Resolve bet' })).not.toBeInTheDocument();
	});

	it('shows the error when the reload finds the User is no longer the Decider', async () => {
		page.data.user = { id: 'u2', name: 'Bruno' };
		page.form = { action: 'resolve', betId: 'b1', error: 'Only the Decider can resolve.' };
		const screen = await render(ResolveControl, { bet });
		await expect.element(screen.getByRole('alert')).toHaveTextContent('Only the Decider can resolve.');
		await expect.element(screen.getByRole('button', { name: 'Resolve bet' })).not.toBeInTheDocument();
	});
});
