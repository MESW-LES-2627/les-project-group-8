/** The login page, set to bring the visitor back to `from` (path and query) afterwards. */
export function loginPath(from: URL): string {
	return `/login?redirectTo=${encodeURIComponent(from.pathname + from.search)}`;
}

/**
 * `target` if it is a path on this site, otherwise `/`. Keeps `?redirectTo=` from
 * sending people to another site after they log in (open redirect): `https://evil.com`,
 * `//evil.com` and `/\evil.com` all resolve to another origin and are ignored.
 */
export function sameSitePath(target: string | null, base: URL): string {
	if (!target?.startsWith('/')) return '/';
	try {
		const url = new URL(target, base);
		return url.origin === base.origin ? url.pathname + url.search + url.hash : '/';
	} catch {
		return '/';
	}
}
