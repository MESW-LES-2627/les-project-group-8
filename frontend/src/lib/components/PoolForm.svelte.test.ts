import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import { toLocalInput } from '#lib/format.ts';
import PoolForm from './PoolForm.svelte';
import { finishSubmit } from './form-actions.mock.ts';

vi.mock('$app/forms', () => import('./form-actions.mock.ts'));

const NOW = new Date('2026-03-10T09:30:00Z').getTime();
const HOUR = 60 * 60 * 1000;
const inLocalInput = (offsetMs: number) => toLocalInput(new Date(NOW + offsetMs).toISOString());

describe('PoolForm', () => {
	beforeEach(() => {
		// Only Date: real timers keep `expect.element` polling.
		vi.useFakeTimers({ toFake: ['Date'] });
		vi.setSystemTime(NOW);
	});
	afterEach(() => {
		vi.useRealTimers();
	});

	it('starts empty with the deadline one day from now', async () => {
		const screen = await render(PoolForm);
		await expect.element(screen.getByLabelText('Name')).toHaveValue('');
		await expect.element(screen.getByLabelText('Deadline')).toHaveValue(inLocalInput(24 * HOUR));
		await expect.element(screen.getByRole('alert')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('button', { name: 'Create pool' })).toBeEnabled();
	});

	it.each([
		['+1 hour', HOUR],
		['+1 day', 24 * HOUR],
		['+1 week', 7 * 24 * HOUR]
	])('sets the deadline with the %s preset', async (name, offset) => {
		const screen = await render(PoolForm);
		await screen.getByLabelText('Deadline').fill('2030-01-01T12:00');
		await screen.getByRole('button', { name }).click();
		await expect.element(screen.getByLabelText('Deadline')).toHaveValue(inLocalInput(offset));
	});

	it('disables the button while creating', async () => {
		const screen = await render(PoolForm);
		await screen.getByLabelText('Name').fill('Derby');
		await screen.getByRole('button', { name: 'Create pool' }).click();
		await expect.element(screen.getByRole('button', { name: 'Creating…' })).toBeDisabled();
		await finishSubmit('success');
		await expect.element(screen.getByRole('button', { name: 'Create pool' })).toBeEnabled();
	});

	it('posts the deadline as UTC ISO', async () => {
		const screen = await render(PoolForm);
		const deadline = screen.getByLabelText('Deadline');
		await deadline.fill('2030-01-01T12:00');
		const input = deadline.element() as HTMLInputElement;
		// Building FormData fires the `formdata` event, as a real submit does.
		const posted = new FormData(input.form!).get('deadline');
		expect(posted).toBe(new Date('2030-01-01T12:00').toISOString());
	});

	it('restores a failed submission with its errors', async () => {
		const deadline = '2030-01-01T12:00:00.000Z';
		const screen = await render(PoolForm, {
			form: {
				error: 'Fix the highlighted fields.',
				fields: {
					name: 'Name is required.',
					description: 'Description is too long.',
					deadline: 'Deadline must be in the future.'
				},
				values: { name: 'Derby', description: 'Weekend games', deadline }
			}
		});
		await expect.element(screen.getByRole('alert')).toHaveTextContent('Fix the highlighted fields.');
		await expect.element(screen.getByLabelText('Name')).toHaveValue('Derby');
		await expect.element(screen.getByLabelText('Name')).toHaveAttribute('aria-invalid', 'true');
		await expect.element(screen.getByLabelText('Description (optional)')).toHaveValue('Weekend games');
		// The submitted deadline stays instead of the one-day default.
		await expect.element(screen.getByLabelText('Deadline')).toHaveValue(toLocalInput(deadline));
		for (const message of ['Name is required.', 'Description is too long.', 'Deadline must be in the future.']) {
			await expect.element(screen.getByText(message)).toBeVisible();
		}
	});
});
