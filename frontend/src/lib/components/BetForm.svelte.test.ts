import { describe, expect, it, vi } from 'vitest';
import { render } from 'vitest-browser-svelte';
import BetForm from './BetForm.svelte';
import { finishSubmit } from './form-actions.mock.ts';

vi.mock('$app/forms', () => import('./form-actions.mock.ts'));

describe('BetForm', () => {
	it('starts with two empty options, radio buttons and no errors', async () => {
		const screen = await render(BetForm);
		await expect.element(screen.getByLabelText('Option 1')).toHaveValue('');
		await expect.element(screen.getByLabelText('Option 2')).toHaveValue('');
		await expect.element(screen.getByLabelText('Option 3')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('button', { name: 'Remove' })).not.toBeInTheDocument();
		await expect.element(screen.getByRole('radio', { name: 'Radio buttons' })).toBeChecked();
		await expect.element(screen.getByRole('alert')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('button', { name: 'Add bet' })).toBeEnabled();
	});

	it('hides the options and presentation for a free-text Bet', async () => {
		const screen = await render(BetForm);
		await expect.element(screen.getByRole('radio', { name: 'Multiple choice' })).toBeChecked();
		await screen.getByRole('radio', { name: 'Free text' }).click();
		await expect.element(screen.getByLabelText('Option 1')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('radio', { name: 'Radio buttons' })).not.toBeInTheDocument();
		await screen.getByRole('radio', { name: 'Multiple choice' }).click();
		await expect.element(screen.getByLabelText('Option 1')).toBeVisible();
	});

	it('restores a failed free-text submission as free text', async () => {
		const screen = await render(BetForm, {
			form: { error: 'Statement cannot be empty.', values: { statement: '', answer_type: 'text', options: [], presentation: '' } }
		});
		await expect.element(screen.getByRole('radio', { name: 'Free text' })).toBeChecked();
		await expect.element(screen.getByLabelText('Option 1')).not.toBeInTheDocument();
	});

	it('adds options up to ten', async () => {
		const screen = await render(BetForm);
		const add = screen.getByRole('button', { name: '+ Add option' });
		for (let count = 3; count <= 10; count++) {
			await add.click();
			await expect.element(screen.getByLabelText(`Option ${count}`)).toBeVisible();
		}
		await expect.element(add).not.toBeInTheDocument();
	});

	it('removes the chosen option and keeps at least two', async () => {
		const screen = await render(BetForm);
		await screen.getByRole('button', { name: '+ Add option' }).click();
		await screen.getByLabelText('Option 1').fill('Porto');
		await screen.getByLabelText('Option 2').fill('Benfica');
		await screen.getByLabelText('Option 3').fill('Sporting');
		await screen.getByRole('button', { name: 'Remove' }).nth(1).click();
		await expect.element(screen.getByLabelText('Option 1')).toHaveValue('Porto');
		await expect.element(screen.getByLabelText('Option 2')).toHaveValue('Sporting');
		await expect.element(screen.getByLabelText('Option 3')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('button', { name: 'Remove' })).not.toBeInTheDocument();
	});

	it('disables the button while adding', async () => {
		const screen = await render(BetForm);
		await screen.getByLabelText('Bet statement').fill('Who wins?');
		await screen.getByLabelText('Option 1').fill('Porto');
		await screen.getByLabelText('Option 2').fill('Benfica');
		await screen.getByRole('button', { name: 'Add bet' }).click();
		await expect.element(screen.getByRole('button', { name: 'Adding…' })).toBeDisabled();
		await finishSubmit('success');
		await expect.element(screen.getByRole('button', { name: 'Add bet' })).toBeEnabled();
	});

	it('restores a failed submission with its errors', async () => {
		const screen = await render(BetForm, {
			form: {
				error: 'Fix the highlighted fields.',
				fields: {
					statement: 'Statement is required.',
					options: 'Options must be different.',
					presentation: 'Pick a presentation.'
				},
				values: { statement: 'Who wins?', options: ['A', 'A', 'B'], presentation: 'dropdown' }
			}
		});
		await expect.element(screen.getByRole('alert')).toHaveTextContent('Fix the highlighted fields.');
		const statement = screen.getByLabelText('Bet statement');
		await expect.element(statement).toHaveValue('Who wins?');
		await expect.element(statement).toHaveAttribute('aria-invalid', 'true');
		await expect.element(screen.getByText('Statement is required.')).toBeVisible();
		await expect.element(screen.getByLabelText('Option 3')).toHaveValue('B');
		await expect.element(screen.getByLabelText('Option 1')).toHaveAttribute('aria-invalid', 'true');
		await expect.element(screen.getByText('Options must be different.')).toBeVisible();
		await expect.element(screen.getByRole('radio', { name: 'Dropdown' })).toBeChecked();
		await expect.element(screen.getByText('Pick a presentation.')).toBeVisible();
	});

	it('starts a fresh Bet after one is added', async () => {
		const screen = await render(BetForm, {
			form: { values: { statement: 'Who wins?', options: ['A', 'B', 'C'], presentation: 'dropdown' } }
		});
		await screen.rerender({ form: { added: true } });
		await expect.element(screen.getByLabelText('Bet statement')).toHaveValue('');
		await expect.element(screen.getByLabelText('Option 1')).toHaveValue('');
		await expect.element(screen.getByLabelText('Option 3')).not.toBeInTheDocument();
		await expect.element(screen.getByRole('radio', { name: 'Radio buttons' })).toBeChecked();
	});
});
