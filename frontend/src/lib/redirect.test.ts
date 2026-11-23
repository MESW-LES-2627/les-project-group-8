import { describe, expect, it } from 'vitest';
import { loginPath, sameSitePath } from './redirect.ts';

const base = new URL('https://bets.example/pools/1');

describe('loginPath', () => {
	it('keeps the path and query, encoded', () => {
		expect(loginPath(new URL('https://bets.example/pools/7?created=1'))).toBe(
			'/login?redirectTo=%2Fpools%2F7%3Fcreated%3D1'
		);
	});
});

describe('sameSitePath', () => {
	it.each(['https://evil.com', '//evil.com', '/\\evil.com', 'pools/1', '', null])(
		'sends %j home',
		(target) => {
			expect(sameSitePath(target, base)).toBe('/');
		}
	);

	it('keeps a same-site path with query and hash', () => {
		expect(sameSitePath('/pools/7?created=1#bets', base)).toBe('/pools/7?created=1#bets');
	});
});
