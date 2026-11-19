// New-Pool rules, shared by the action's checks and the form's maxlength.
import type { CreatePoolInput } from '#lib/types.ts';

export const POOL_NAME_MAX = 120;
export const POOL_DESCRIPTION_MAX = 500;

export type PoolFieldErrors = {
	name?: string;
	description?: string;
	deadline?: string;
};

/** Checks a new Pool; `input` (with the deadline as UTC ISO) is set only when there are no errors. */
export function validatePool(values: CreatePoolInput): { errors: PoolFieldErrors; input?: CreatePoolInput } {
	const errors: PoolFieldErrors = {};

	if (!values.name) {
		errors.name = 'Name cannot be empty.';
	} else if (values.name.length > POOL_NAME_MAX) {
		errors.name = `Name must be at most ${POOL_NAME_MAX} characters.`;
	}

	if (values.description.length > POOL_DESCRIPTION_MAX) {
		errors.description = `Description must be at most ${POOL_DESCRIPTION_MAX} characters.`;
	}

	let deadline = '';
	if (!values.deadline) {
		errors.deadline = 'Choose a deadline.';
	} else {
		const date = new Date(values.deadline);
		if (Number.isNaN(date.getTime())) {
			errors.deadline = 'Deadline is not a valid date.';
		} else if (date.getTime() <= Date.now()) {
			errors.deadline = 'Deadline must be in the future.';
		} else {
			deadline = date.toISOString();
		}
	}

	if (Object.keys(errors).length > 0) {
		return { errors };
	}
	return { errors, input: { ...values, deadline } };
}
