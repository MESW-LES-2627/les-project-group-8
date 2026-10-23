import { fail, redirect } from '@sveltejs/kit';
import { ApiError, createPool } from '../../../lib/server/api';
import type { CreatePoolInput } from '../../../lib/types';

type FieldErrors = {
	name?: string;
	statement?: string;
	option1?: string;
	option2?: string;
	deadline?: string;
};

function read(form: FormData, key: string): string {
	const value = form.get(key);
	return typeof value === 'string' ? value.trim() : '';
}

function validate(values: {
	name: string;
	statement: string;
	deadline: string;
	option1: string;
	option2: string;
}): { errors: FieldErrors; input?: CreatePoolInput } {
	const errors: FieldErrors = {};

	if (!values.name) {
		errors.name = 'Name cannot be empty.';
	} else if (values.name.length > 120) {
		errors.name = 'Name must be at most 120 characters.';
	}

	if (!values.statement) {
		errors.statement = 'Statement cannot be empty.';
	} else if (values.statement.length > 500) {
		errors.statement = 'Statement must be at most 500 characters.';
	}

	if (!values.option1) {
		errors.option1 = 'Option A cannot be empty.';
	} else if (values.option1.length > 100) {
		errors.option1 = 'Option A must be at most 100 characters.';
	}

	if (!values.option2) {
		errors.option2 = 'Option B cannot be empty.';
	} else if (values.option2.length > 100) {
		errors.option2 = 'Option B must be at most 100 characters.';
	}

	if (
		!errors.option1 &&
		!errors.option2 &&
		values.option1.toLowerCase() === values.option2.toLowerCase()
	) {
		errors.option2 = 'Options must be different.';
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

	return {
		errors,
		input: {
			name: values.name,
			statement: values.statement,
			deadline,
			options: [values.option1, values.option2]
		}
	};
}

export const actions = {
	default: async ({ request }) => {
		const form = await request.formData();
		const values = {
			name: read(form, 'name'),
			statement: read(form, 'statement'),
			deadline: read(form, 'deadline'),
			option1: read(form, 'option1'),
			option2: read(form, 'option2')
		};

		const { errors, input } = validate(values);
		if (!input) {
			return fail(400, { error: 'Please fix the errors below.', fields: errors, values });
		}

		try {
			await createPool(input);
		} catch (error) {
			if (error instanceof ApiError && error.status === 400) {
				return fail(400, { error: error.message, values });
			}
			return fail(502, {
				error: error instanceof Error ? error.message : 'Could not save the pool.',
				values
			});
		}

		redirect(303, '/?created=1');
	}
};
