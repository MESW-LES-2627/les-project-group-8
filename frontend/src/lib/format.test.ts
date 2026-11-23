import { describe, expect, it } from 'vitest';
import { formatDeadline, localInputToIso, toLocalInput } from './format.ts';

describe('formatDeadline', () => {
	it('formats an ISO timestamp in UTC', () => {
		expect(formatDeadline('2026-12-01T18:05:00Z')).toBe('01 Dec 2026, 18:05 UTC');
	});

	it('returns an invalid ISO string unchanged', () => {
		expect(formatDeadline('not a date')).toBe('not a date');
	});
});

describe('toLocalInput and localInputToIso', () => {
	it('round-trip a timestamp to the minute in any timezone', () => {
		const iso = '2026-12-01T18:05:00.000Z';
		expect(toLocalInput(iso)).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/);
		expect(localInputToIso(toLocalInput(iso))).toBe(iso);
	});

	it('toLocalInput returns an empty string for an invalid ISO', () => {
		expect(toLocalInput('nope')).toBe('');
	});

	it('localInputToIso returns null for empty or invalid input', () => {
		expect(localInputToIso('')).toBeNull();
		expect(localInputToIso('nope')).toBeNull();
	});
});
