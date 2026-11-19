# The Playwright e2e harness on a local Supabase, proven by sign-up

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement` and
  `code-review` skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills), Supabase
  CLI 3.2.0, Playwright 1.65.1.
- **Outcome:** the e2e harness for
  [#122](https://github.com/MESW-LES-2627/les-project-group-8/issues/122):
  `supabase/config.toml`, `frontend/e2e/run.sh`, `frontend/playwright.config.ts`,
  `frontend/e2e/signup.spec.ts` (US5) and `.github/workflows/e2e.yml`.
- **Delegated:** installing the Supabase CLI; the ES256 check first (the local
  JWKS serves an ES256 key, Flask's `TokenVerifier` returns 200 for a local
  token and 401 for a forged one, and supabase-js `getClaims` accepts the
  local token and rejects the forged one with "Invalid JWT signature");
  writing the run script, the config, the spec, the workflow and the docs.
- **Where it was wrong:** `supabase gen signing-key` in CLI 3.x writes into the
  configured key file and fails if it is missing or not a JSON array, not to
  stdout as the plan assumed; the script seeds the file with `[]` and uses
  `--append`.
- **How we checked:** `pnpm test:e2e` passes locally from a fresh stack, and the
  stack is gone afterwards; with the header changed to show another name, the
  spec fails; `pnpm check`, the 35 Vitest tests and the 155 backend tests pass;
  `vite preview` uses the exported local Supabase URL rather than
  `wrangler.jsonc`'s hosted one (the probe sign-up landed in the local
  `auth.users`). The CI workflow has not run yet.
- **Notes:** without the exported env, `vite preview` would likely fall back to
  `wrangler.jsonc`'s vars, the hosted project (inferred, not tried), so
  `playwright.config.ts` refuses to run without a local `SUPABASE_URL`.
