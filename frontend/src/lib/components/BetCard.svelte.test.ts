import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import type { Bet, Pick } from '#lib/types.ts';
import BetCard from './BetCard.svelte';
import { finishSubmit, invalidateAll } from './form-actions.mock.ts';

// BetCard's children read `page`; an empty page hides them, so these tests see BetCard alone.
vi.mock('$app/state', () => ({ page: { data: {}, form: null } }));
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
const user = { id: 'u1', name: 'Ana' };
const pick: Pick = { id: 'k1', bet_id: 'b1', user_id: 'u1', user, outcome_id: 'o2', created_at: '' };
const base = { bet, poolStatus: 'OPEN' as const, loggedIn: true, user, loginHref: '/login?next=/pools/p1' };

describe('BetCard', () => {
	beforeEach(() => {
		invalidateAll.mockClear();
	});

	describe('while picks are open', () => {
		it('offers radio buttons with nothing picked yet', async () => {
			const screen = await render(BetCard, base);
			await expect.element(screen.getByRole('radio', { name: 'Porto' })).not.toBeChecked();
			await expect.element(screen.getByRole('radio', { name: 'Benfica' })).not.toBeChecked();
			await expect.element(screen.getByRole('button', { name: 'Save pick' })).toBeEnabled();
			await expect.element(screen.getByText('Saved:')).not.toBeInTheDocument();
		});

		it('checks and labels the saved pick', async () => {
			const screen = await render(BetCard, { ...base, pick });
			// The saved option's label carries a "Your pick" tag.
			await expect.element(screen.getByRole('radio', { name: 'Benfica Your pick' })).toBeChecked();
			await expect.element(screen.getByRole('radio', { name: 'Porto', exact: true })).not.toBeChecked();
			await expect.element(screen.getByText('Saved: Benfica')).toBeVisible();
			await expect.element(screen.getByRole('button', { name: 'Change pick' })).toBeVisible();
		});

		it('offers a dropdown when the Bet asks for one', async () => {
			const screen = await render(BetCard, { ...base, bet: { ...bet, presentation: 'dropdown' }, pick });
			await expect.element(screen.getByRole('combobox', { name: 'Your pick' })).toHaveValue('o2');
			await expect.element(screen.getByRole('radio')).not.toBeInTheDocument();
		});

		it('keeps the submitted option and shows the error after a failed save', async () => {
			const screen = await render(BetCard, { ...base, pick, form: { error: 'Picks are closed.', outcomeId: 'o1' } });
			await expect.element(screen.getByRole('alert')).toHaveTextContent('Picks are closed.');
			await expect.element(screen.getByRole('radio', { name: 'Porto' })).toBeChecked();
		});

		it('confirms a saved pick', async () => {
			const screen = await render(BetCard, { ...base, pick, form: { saved: true } });
			await expect.element(screen.getByRole('status')).toHaveTextContent('Pick saved.');
		});

		it.each([
			['reloads the page after a failed save', 'failure', 1],
			['keeps the page after a successful save', 'success', 0]
		] as const)('disables the button while saving and %s', async (_, type, reloads) => {
			const screen = await render(BetCard, base);
			await screen.getByRole('radio', { name: 'Porto' }).click();
			await screen.getByRole('button', { name: 'Save pick' }).click();
			await expect.element(screen.getByRole('button', { name: 'Saving…' })).toBeDisabled();
			await finishSubmit(type);
			await expect.element(screen.getByRole('button', { name: 'Save pick' })).toBeEnabled();
			expect(invalidateAll).toHaveBeenCalledTimes(reloads);
		});

		it('asks a visitor to log in', async () => {
			const screen = await render(BetCard, { ...base, loggedIn: false, user: null });
			await expect.element(screen.getByText('Log in to save your pick.')).toBeVisible();
			await expect.element(screen.getByRole('link', { name: 'Log in' })).toHaveAttribute('href', base.loginHref);
			await expect.element(screen.getByText('Picks are closed.')).not.toBeInTheDocument();
			await expect.element(screen.getByRole('radio')).not.toBeInTheDocument();
		});

		it('sends an Account with no User profile to /no-user', async () => {
			const screen = await render(BetCard, { ...base, user: null });
			await expect.element(screen.getByText('This account has no User profile yet.')).toBeVisible();
			await expect.element(screen.getByRole('link', { name: 'What now?' })).toHaveAttribute('href', '/no-user');
		});
	});

	describe('once picks are closed', () => {
		const locked = { ...base, poolStatus: 'LOCKED' as const };

		it("shows the User's pick and no form", async () => {
			const screen = await render(BetCard, { ...locked, pick });
			await expect.element(screen.getByText('Picks are closed.')).toBeVisible();
			await expect.element(screen.getByText('Your pick: Benfica')).toBeVisible();
			await expect.element(screen.getByRole('radio')).not.toBeInTheDocument();
		});

		it('says so when the User did not pick', async () => {
			const screen = await render(BetCard, locked);
			await expect.element(screen.getByText('You did not pick an option.')).toBeVisible();
		});

		it('asks a visitor to log in to see their pick', async () => {
			const screen = await render(BetCard, { ...locked, loggedIn: false, user: null });
			await expect.element(screen.getByText('Log in to see your saved pick.')).toBeVisible();
		});

		it('marks the winner of a resolved Bet, even while the Pool is open', async () => {
			const screen = await render(BetCard, { ...base, bet: { ...bet, winning_outcome_id: 'o1' } });
			await expect.element(screen.getByRole('listitem').filter({ hasText: 'Porto' })).toHaveTextContent('Porto Winner');
			await expect.element(screen.getByRole('listitem').filter({ hasText: 'Benfica' })).toHaveTextContent('Benfica');
			await expect.element(screen.getByText('Picks are closed.')).toBeVisible();
		});
	});
});
