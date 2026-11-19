import type { CreatePoolInput } from '#lib/types.ts';

export type FieldErrors = {
	name?: string;
	description?: string;
	deadline?: string;
};

export function validate(values: CreatePoolInput): { errors: FieldErrors; input?: CreatePoolInput } {
	const errors: FieldErrors = {};

	if (!values.name) {
		errors.name = 'Name cannot be empty.';
	} else if (values.name.length > 120) {
		errors.name = 'Name must be at most 120 characters.';
	}

	if (values.description.length > 500) {
		errors.description = 'Description must be at most 500 characters.';
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
