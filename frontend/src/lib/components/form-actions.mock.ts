import { vi } from 'vitest';

// Stands in for `$app/forms` and `$app/navigation` in component tests:
// a submit stays pending until the test calls `finishSubmit`.
let pendingSubmit: ((opts: { update: () => Promise<void>; result: { type: string } }) => Promise<void>) | undefined;

export const invalidateAll = vi.fn();

export function enhance(form: HTMLFormElement, submit: () => typeof pendingSubmit) {
	const onSubmit = (event: SubmitEvent) => {
		event.preventDefault();
		pendingSubmit = submit();
	};
	form.addEventListener('submit', onSubmit);
	return { destroy: () => form.removeEventListener('submit', onSubmit) };
}

export async function finishSubmit(type: 'success' | 'failure') {
	await pendingSubmit?.({ update: async () => {}, result: { type } });
}
