import { fail, redirect } from '@sveltejs/kit';
import { readField } from '#lib/form.ts';
import { loginPath } from '#lib/redirect.ts';
import { ApiError, createPool } from '#lib/server/api.ts';
import { endSession } from '#lib/server/session.ts';
import type { CreatePoolInput, PoolPresentation } from '#lib/types.ts';

const MIN_OPTIONS = 2;
const MAX_OPTIONS = 10;

type FieldErrors = {
	name?: string;
	statement?: string;
	options?: string;
	deadline?: string;
};

type FormValues = {
	name: string;
	statement: string;
	deadline: string;
	options: string[];
	presentation: string;
};

function read(form: FormData, key: string): string {
	return readField(form, key).trim();
}

function readOptions(form: FormData): string[] {
	return form.getAll('options').map((value) => (typeof value === 'string' ? value.trim() : ''));
}

function validate(values: FormValues): { errors: FieldErrors; input?: CreatePoolInput } {
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

	if (values.options.length < MIN_OPTIONS) {
		errors.options = 'Add at least two options.';
	} else if (values.options.length > MAX_OPTIONS) {
		errors.options = `Use at most ${MAX_OPTIONS} options.`;
	} else if (values.options.some((option) => !option)) {
		errors.options = 'Every option needs a label.';
	} else if (values.options.some((option) => option.length > 100)) {
		errors.options = 'Options must be at most 100 characters.';
	} else if (
		new Set(values.options.map((option) => option.toLowerCase())).size !== values.options.length
	) {
		errors.options = 'Options must be different.';
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

	const presentation: PoolPresentation = values.presentation === 'dropdown' ? 'dropdown' : 'radio';

	return {
		errors,
		input: {
			name: values.name,
			statement: values.statement,
			deadline,
			options: values.options,
			presentation
		}
	};
}

// Creating a pool needs a logged-in User: Flask makes them its creator and decider.
export function load({ locals, url }) {
	if (!locals.session) redirect(303, loginPath(url));
}

export const actions = {
	default: async ({ request, locals, cookies, url }) => {
		// The session may have ended since the page loaded (logged out in another tab, or not renewable).
		if (!locals.session) redirect(303, loginPath(url));

		const form = await request.formData();
		const values: FormValues = {
			name: read(form, 'name'),
			statement: read(form, 'statement'),
			deadline: read(form, 'deadline'),
			options: readOptions(form),
			presentation: read(form, 'presentation')
		};

		const { errors, input } = validate(values);
		if (!input) {
			return fail(400, { error: 'Please fix the errors below.', fields: errors, values });
		}

		try {
			await createPool(input, locals.session.access_token);
		} catch (error) {
			if (error instanceof ApiError && error.status === 401) {
				// Flask refused the token. End the session too, or /login would send a
				// still-"logged-in" visitor straight home. The half-filled form is lost.
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			if (error instanceof ApiError && error.status === 403) {
				// A valid token, but its Account has no User: logging in again won't help.
				redirect(303, '/no-user');
			}
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
