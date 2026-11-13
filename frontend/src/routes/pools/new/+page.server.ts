import { fail, redirect } from '@sveltejs/kit';
import { readField } from '#lib/form.ts';
import { loginPath } from '#lib/redirect.ts';
import { ApiError, createPool } from '#lib/server/api.ts';
import { endSession } from '#lib/server/session.ts';
import type { CreatePoolInput, Pool } from '#lib/types.ts';

type FieldErrors = {
	name?: string;
	description?: string;
	deadline?: string;
};

function validate(values: CreatePoolInput): { errors: FieldErrors; input?: CreatePoolInput } {
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

export function load({
	locals,
	url
}) {
	if (!locals.session) {
		redirect(303, loginPath(url));
	}
}

export const actions = {
	default: async ({
		request,
		locals,
		cookies,
		url
	}) => {
		if (!locals.session) {
			redirect(303, loginPath(url));
		}

		const form = await request.formData();
		const values = {
			name: readField(form, 'name').trim(),
			description: readField(form, 'description').trim(),
			deadline: readField(form, 'deadline').trim()
		};
		const { errors, input } = validate(values);
		if (!input) {
			return fail(400, {
				error: 'Please fix the errors below.',
				fields: errors,
				values
			});
		}

		let pool: Pool;
		try {
			pool = await createPool(input, locals.session.access_token);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			if (err instanceof ApiError && err.status === 403) {
				redirect(303, '/no-user');
			}
			if (err instanceof ApiError && err.status === 400) {
				return fail(400, { error: err.message, values });
			}
			return fail(502, {
				error: err instanceof Error ? err.message : 'Could not save the pool.',
				values
			});
		}

		redirect(303, `/pools/${pool.id}?created=1`);
	}
};
