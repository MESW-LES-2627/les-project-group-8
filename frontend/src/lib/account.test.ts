import { describe, expect, it } from 'vitest';
import { validateName } from './account.ts';

describe('validateName', () => {
	it('accepts a 1-character name', () => {
		expect(validateName('A')).toEqual({ name: 'A' });
	});

	it('accepts an 80-character name', () => {
		expect(validateName('n'.repeat(80))).toEqual({ name: 'n'.repeat(80) });
	});

	it('trims the name before checking and saving it', () => {
		expect(validateName('  Ana  ')).toEqual({ name: 'Ana' });
	});

	it.each([
		['', 'Name cannot be empty.'],
		['   ', 'Name cannot be empty.'],
		[' \t\r\n ', 'Name cannot be empty.'],
		['n'.repeat(81), 'Name must be at most 80 characters.']
	])('rejects %j', (raw, error) => {
		expect(validateName(raw)).toEqual({ name: raw.trim(), error });
	});
});
