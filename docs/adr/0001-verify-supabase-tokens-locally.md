# Verify Supabase access tokens locally in Flask

The SvelteKit server forwards the logged-in Account's Supabase access token to Flask as `Authorization: Bearer <token>`. Flask verifies it itself instead of asking Supabase on every request: it fetches the project's public signing key once from `<SUPABASE_URL>/auth/v1/.well-known/jwks.json` (ES256), caches it, and with PyJWT checks the signature, that `exp` has not passed, and that `aud` is `authenticated`. If all three pass, the token's `sub` is the trusted id of the User; otherwise Flask answers 401.

Think of the token as a stamped ID card: Supabase stamps it with a private key only it holds, and the public key lets Flask check the stamp without phoning the issuer. That keeps every request free of an extra Render → Supabase round trip and keeps Flask working if Supabase Auth is briefly unreachable.

## Considered Options

- **Ask Supabase each time** (`auth.get_user(token)`): always reflects the live state of the Account, but adds a network call and a dependency on Supabase Auth to every authenticated request.
- **Legacy HS256 shared secret**: the project has already moved to asymmetric signing keys, and sharing the secret would let Flask mint tokens, not just check them.

## Consequences

- Banning or deleting an Account does not cut off tokens it already holds; they stay valid until they expire (1 hour by default). Acceptable for a class demo; revisit if instant revocation matters.
- When Supabase rotates its signing key, Flask must refetch the key set on an unknown `kid` instead of only at startup.
