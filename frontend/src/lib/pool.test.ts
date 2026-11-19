import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { validate } from './pool.ts';

const valid = { name: 'World Cup', description: '', deadline: '2026-12-01T18:00:00.000Z' };

describe('validate', () => {
	beforeEach(() => {
		vi.useFakeTimers();
		vi.setSystemTime(new Date('2026-11-19T12:00:00Z'));
	});

	afterEach(() => {
		vi.useRealTimers();
	});

	it('accepts a valid pool and normalizes the deadline to ISO', () => {
		const deadline = '2026-12-01T18:00:00+01:00';
		expect(validate({ ...valid, deadline })).toEqual({
			errors: {},
			input: { ...valid, deadline: '2026-12-01T17:00:00.000Z' }
		});
	});

	it('accepts a 120-character name and a 500-character description', () => {
		const result = validate({ ...valid, name: 'n'.repeat(120), description: 'd'.repeat(500) });
		expect(result.errors).toEqual({});
		expect(result.input).toBeDefined();
	});

	it.each([
		[{ name: '' }, { name: 'Name cannot be empty.' }],
		[{ name: 'n'.repeat(121) }, { name: 'Name must be at most 120 characters.' }],
		[{ description: 'd'.repeat(501) }, { description: 'Description must be at most 500 characters.' }],
		[{ deadline: '' }, { deadline: 'Choose a deadline.' }],
		[{ deadline: 'soon' }, { deadline: 'Deadline is not a valid date.' }],
		[{ deadline: '2026-11-19T12:00:00Z' }, { deadline: 'Deadline must be in the future.' }],
		[{ deadline: '2026-11-18T12:00:00Z' }, { deadline: 'Deadline must be in the future.' }]
	])('rejects %j', (change, errors) => {
		expect(validate({ ...valid, ...change })).toEqual({ errors });
	});

	it('reports every invalid field at once', () => {
		expect(Object.keys(validate({ name: '', description: 'd'.repeat(501), deadline: '' }).errors))
			.toEqual(['name', 'description', 'deadline']);
	});
});
