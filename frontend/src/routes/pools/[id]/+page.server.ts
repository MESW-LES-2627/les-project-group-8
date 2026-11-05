import { error, fail, redirect } from '@sveltejs/kit';
import { readField } from '#lib/form.ts';
import { loginPath } from '#lib/redirect.ts';
import { ApiError, createBet, getMyPicks, getPool, savePick } from '#lib/server/api.ts';
import { clearSessionCookies, endSession } from '#lib/server/session.ts';
import type { BetPresentation, CreateBetInput, Pick, Pool } from '#lib/types.ts';

type BetValues = {
	statement: string;
	options: string[];
	presentation: string;
};

type BetErrors = {
	statement?: string;
	options?: string;
	presentation?: string;
};

function validateBet(values: BetValues): { fields: BetErrors; input?: CreateBetInput } {
	const fields: BetErrors = {};

	if (!values.statement) {
		fields.statement = 'Statement cannot be empty.';
	} else if (values.statement.length > 500) {
		fields.statement = 'Statement must be at most 500 characters.';
	}

	if (values.options.length < 2 || values.options.length > 10) {
		fields.options = 'Add between 2 and 10 options.';
	} else if (values.options.some((option) => !option)) {
		fields.options = 'Every option needs a label.';
	} else if (values.options.some((option) => option.length > 100)) {
		fields.options = 'Options must be at most 100 characters.';
	} else if (
		new Set(values.options.map((option) => option.toLowerCase())).size !== values.options.length
	) {
		fields.options = 'Options must be different.';
	}

	if (values.presentation !== 'radio' && values.presentation !== 'dropdown') {
		fields.presentation = 'Choose radio buttons or a dropdown.';
	}

	const presentation: BetPresentation = values.presentation === 'dropdown' ? 'dropdown' : 'radio';
	if (Object.keys(fields).length > 0) {
		return { fields };
	}
	return { fields, input: { ...values, presentation } };
}

export async function load({
	params,
	locals,
	cookies,
	url
}) {
	let pool: Pool;
	try {
		pool = await getPool(params.id);
	} catch (err) {
		if (err instanceof ApiError && err.status === 404) {
			throw error(404, 'Pool not found');
		}
		return {
			pool: null,
			picks: [] as Pick[],
			pickLoadError: null,
			created: false,
			loadError: err instanceof Error ? err.message : 'Could not load the pool.'
		};
	}

	let picks: Pick[] = [];
	let pickLoadError: string | null = null;
	if (locals.session) {
		try {
			picks = await getMyPicks(pool.id, locals.session.access_token);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				clearSessionCookies(cookies);
				locals.session = null;
			} else if (!(err instanceof ApiError && err.status === 403)) {
				pickLoadError = err instanceof Error ? err.message : 'Could not load your picks.';
			}
		}
	}

	return {
		pool,
		picks,
		pickLoadError,
		loadError: null,
		created: url.searchParams.has('created')
	};
}

export const actions = {
	addBet: async ({
		params,
		request,
		locals,
		cookies,
		url
	}) => {
		if (!locals.session) {
			redirect(303, loginPath(url));
		}

		const form = await request.formData();
		const values: BetValues = {
			statement: readField(form, 'statement').trim(),
			options: form.getAll('options').map((value) =>
				typeof value === 'string' ? value.trim() : ''
			),
			presentation: readField(form, 'presentation') || 'radio'
		};
		const { fields, input } = validateBet(values);
		if (!input) {
			return fail(400, {
				action: 'addBet' as const,
				error: 'Please fix the errors below.',
				fields,
				values
			});
		}

		try {
			await createBet(
				params.id,
				input,
				locals.session.access_token
			);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			// A 403 here can mean a different owner, so show the explanation instead of /no-user.
			if (err instanceof ApiError && [400, 403, 404].includes(err.status)) {
				return fail(err.status, {
					action: 'addBet' as const,
					error: err.message,
					values
				});
			}
			return fail(502, {
				action: 'addBet' as const,
				error: err instanceof Error ? err.message : 'Could not add the bet.',
				values
			});
		}

		return { action: 'addBet' as const, added: true };
	},

	pick: async ({
		params,
		request,
		locals,
		cookies,
		url
	}) => {
		if (!locals.session) {
			redirect(303, loginPath(url));
		}

		const form = await request.formData();
		const betId = readField(form, 'bet_id').trim();
		const outcomeId = readField(form, 'outcome_id').trim();
		if (!betId || !outcomeId) {
			return fail(400, {
				action: 'pick' as const,
				betId,
				outcomeId,
				error: 'Choose an option before saving.'
			});
		}

		try {
			await savePick(
				params.id,
				betId,
				outcomeId,
				locals.session.access_token
			);
		} catch (err) {
			if (err instanceof ApiError && err.status === 401) {
				await endSession(locals, cookies);
				redirect(303, loginPath(url));
			}
			if (err instanceof ApiError && err.status === 403) {
				redirect(303, '/no-user');
			}
			if (err instanceof ApiError && (err.status === 400 || err.status === 404)) {
				return fail(400, {
					action: 'pick' as const,
					betId,
					outcomeId,
					error: err.message
				});
			}
			return fail(502, {
				action: 'pick' as const,
				betId,
				outcomeId,
				error: err instanceof Error ? err.message : 'Could not save your pick.'
			});
		}

		return {
			action: 'pick' as const,
			betId,
			outcomeId,
			saved: true
		};
	}
};
