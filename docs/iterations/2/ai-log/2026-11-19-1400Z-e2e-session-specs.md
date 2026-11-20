# E2E specs for log in, session restored, log out and expired sessions

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5), `implement` and `code-review` skills
  from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills),
  Playwright 1.65.1.
- **Outcome:** `frontend/e2e/session.spec.ts` and the shared helpers in
  `frontend/e2e/account.ts` for
  [#123](https://github.com/MESW-LES-2627/les-project-group-8/issues/123); the
  2.11 row in `i02.d004-testing.md` points at the spec.
- **Delegated:** writing the specs and helpers. The expired and forged
  sessions are set up by rewriting the `sb-<ref>-auth-token` cookie with
  `@supabase/ssr`'s own chunk and base64url helpers: a past `expires_at` with
  an invalid refresh token, and an access token with one signature character
  flipped. The review ran as two sub-agents (standards, spec).
- **Where it was wrong:** the first cookie rewrite took the first `sb-` cookie,
  which wasn't always the session cookie; it now matches the exact name. A
  global Prettier run reformatted the files to double quotes and spaces; that
  was reverted. The spec reviewer reported 4-space indentation in the new
  files, which was false (they use tabs).
- **How we checked:** `pnpm test:e2e` passes (6 specs); a throwaway control spec
  that rewrites the cookie without changing it stays logged in, so the expired
  and forged tests fail for the reason they name; `pnpm check` passes.
- **Notes:** after review, `signup.spec.ts` reuses the `signUp` helper. The
  expired test moves the session's `expires_at`, not the JWT's `exp`:
  `@supabase/auth-js` decides to renew from `expires_at` alone.
