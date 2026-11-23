import { describe, expect, it } from 'vitest';
import { readField } from './form.ts';

describe('readField', () => {
	const form = new FormData();
	form.set('name', 'World Cup');
	form.set('upload', new File(['x'], 'x.txt'));

	it('returns a text field', () => {
		expect(readField(form, 'name')).toBe('World Cup');
	});

	it('returns an empty string for a missing key', () => {
		expect(readField(form, 'missing')).toBe('');
	});

	it('returns an empty string for a file', () => {
		expect(readField(form, 'upload')).toBe('');
	});
});
