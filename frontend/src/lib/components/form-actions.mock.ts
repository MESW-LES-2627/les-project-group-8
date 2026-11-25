import { vi } from 'vitest';

// Stands in for `$app/forms` and `$app/navigation` in component tests:
// a submit stays pending until the test calls `finishSubmit`.
let after: ((opts: { update: () => Promise<void>; result: { type: string } }) => Promise<void>) | undefined;

export const invalidateAll = vi.fn();

export function enhance(form: HTMLFormElement, submit: () => typeof after) {
	const onSubmit = (event: SubmitEvent) => {
		event.preventDefault();
		after = submit();
	};
	form.addEventListener('submit', onSubmit);
	return { destroy: () => form.removeEventListener('submit', onSubmit) };
}

export async function finishSubmit(type: 'success' | 'failure') {
	await after?.({ update: async () => {}, result: { type } });
}
