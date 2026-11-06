# Grilling session: planning authentication (#28)

- **Date:** 2026-11-03, 14:35–15:14.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the `grill-with-docs` skill from Matt Pocock's [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Summary:** see "Planning authentication" in the [iteration 1 AI log](../../../iterations/1/i01.d005-ai-log.md).

This is the conversation as it happened, exported from the Claude Code session log. Messages are copied word for word. The AI's file reads, edits and commands are left out and replaced by short notes in *[brackets]*. In each question, the line starting ➡️ is the AI's recommended answer; Alef's reply comes after each round.

---

### Alef (14:35)

> /mattpocock-skills:grill-with-docs on #28

*[The AI loaded the `grilling` and `domain-modeling` skills, read the backend, frontend and migrations, and fetched the Supabase project's public JWKS.]*

### AI (14:36)

Before the questions, here's what I found in the code and config:

- **Frontend:** SvelteKit running on Cloudflare. The browser never calls Flask; all backend calls go through `src/lib/server/api.ts` on the SvelteKit server.
- **Creating a pool:** the frontend sends `GUEST_USER_ID` as `creator_id` (`frontend/src/lib/constants.ts`). The backend trusts any existing user ID in that field (`backend/pools/service.py:30`).
- **The `users` table** (`id`, `name`, `is_guest`) has no link to Supabase Auth. Anyone can call `POST /api/users` to create a user.
- **Token signing:** your Supabase project already signs tokens with an **asymmetric ES256 key**. Its public key is served at `/auth/v1/.well-known/jwks.json` (I fetched it).
- **Predictions:** there's no endpoint for them yet. The `picks` table exists, but the code that saves picks belongs to US10 in the same iteration.
- **Config mismatch:** `backend/.env.example` says to use the service_role key, but the value in it is a publishable key (`sb_publishable_…`). I'll come back to this later.

---

❓ **Q1** - **Where the login session lives**: The browser never talks to Flask, so the Supabase session has to reach the SvelteKit server somehow. Options:
- (a) Keep the session in httpOnly cookies managed on the SvelteKit server with `@supabase/ssr`. Login and logout are form actions. `hooks.server.ts` restores the session on each request and puts the user in `locals`. `api.ts` sends the access token to Flask as `Authorization: Bearer`.
- (b) Run `supabase-js` in the browser with `localStorage`, and pass the token to the server some other way. That is awkward with form actions, and the page won't know who is logged in on first render.

➡️ Yes to (a): server-side cookie sessions with `@supabase/ssr`, with the token forwarded to Flask as a Bearer header.

---

❓ **Q2** - **How Flask checks the token**: Options:
- (a) Check it inside Flask using the project's public key (JWKS, ES256) with PyJWT. Verify the signature, `exp` and `aud == "authenticated"`, and cache the key. No network call per request.
- (b) Call Supabase's `auth.get_user(token)` on every request. Simpler, but adds latency and depends on Supabase being reachable.
- (c) Use the legacy HS256 shared secret. Your project has already moved off it.

➡️ Yes to (a), behind one small "token verifier" component that tests can replace with a fake.

---

❓ **Q3** - **How a login connects to a person in the app**: Use the same UUID for both, so `users.id` = the Supabase Auth user ID (`sub` in the token). There's no separate mapping column. The backend loads the user with the `sub` from the token, and returns 403 if no matching row exists ("account has no profile").

➡️ Yes: `users.id` = auth user ID. An unknown `sub` gets a 403.

---

❓ **Q4** - **What happens to Guest User**: It is seeded as `0000…0001`, and existing pools point to it. Options:
- (a) Keep the row and its pools as old data that people can still browse. Delete the `GUEST_USER_ID` constant from the frontend. Nothing new is ever written as the guest.
- (b) Give its pools to a real user.
- (c) Delete the guest and its pools.

➡️ Yes to (a). It's the least work, and it keeps public browsing intact.

---

❓ **Q5** - **`creator_id` in the request body**: Once the creator comes from the token, what should the backend do if a request still includes `creator_id`?
- (a) Ignore it silently.
- (b) Reject any request that includes it with a 400.
- (c) Reject it only when it differs from the logged-in user (403).

➡️ Yes to (b). The field leaves the API contract, and "change an ID to impersonate someone" becomes an explicit test that expects a rejection.

---

❓ **Q6** - **"Require login to submit predictions" when no prediction endpoint exists yet**: Should #28 provide a reusable login check (for example a `@require_user` decorator that gives the route the current user), apply it to `POST /api/pools`, and leave applying it to picks to US10? I'd add a note on the issue saying so.

➡️ Yes. The predictions part of #28 is the reusable login check; US10 uses it.

---

❓ **Q7** - **Words for the glossary**: Two pairs of words are used loosely right now:
- "account" vs "application profile" vs "user". I propose two terms. An **Account** is the sign-in identity (email and password in Supabase Auth). A **User** is the person in the app, with a display name, who creates pools and makes picks. Each Account has exactly one User and vice versa.
- "prediction" vs "pick". The backlog, US10 and the `picks` table all say **Pick**. I propose Pick as the standard term, with "prediction" as a word to avoid.

➡️ Yes to both: Account and User as distinct 1:1 terms, and Pick as the standard term.

### Alef (14:43)

> Q1 yes to (a). Before deciding Q2, I need you to clarify (a). Yes to Q3. Q4 yes to (c), the app is only a demo for a class and there is no problem with deleting the guest users. Q5 yes to (b). Q6 yes. Q7 yes to both.

*[The AI wrote `GLOSSARY.md` and read US1 in the user stories.]*

### AI (14:44)

I've created `GLOSSARY.md` with **Account**, **User** and **Pick**.

#### What Q2 (a) means

When someone logs in, Supabase gives the SvelteKit server an **access token**: a short string that says "this is user `<uuid>`, valid until 14:05". Supabase signs it with a **private key** that only Supabase holds. The SvelteKit server sends this token to Flask on every request.

Flask has to be sure two things are true: Supabase really issued the token, and nobody edited it (for example, swapping in someone else's ID). Option (a) does this inside Flask, with no call to Supabase:

1. **Get the public key once.** Supabase publishes the matching public key at `…/auth/v1/.well-known/jwks.json`. A public key can confirm a signature but can't create one, so it's safe to download. Flask fetches it at startup and caches it.
2. **Check every request locally.** PyJWT checks three things, which takes microseconds:
   - the signature matches the public key, so the token wasn't forged or edited;
   - `exp` hasn't passed, so the token isn't expired;
   - `aud` is `authenticated`, so it's a logged-in user's token and not some other kind of Supabase token.
3. **Take the user from the token.** If all three checks pass, the `sub` field is the trusted user ID. If any check fails, Flask returns 401.

It's like a stamped ID card: Flask checks the stamp itself instead of phoning the issuer each time.

**The cost:** if you ban or delete an account, tokens it already holds stay valid until they expire (1 hour by default). For a class demo, that doesn't matter.

**The alternative, option (b):** Flask asks Supabase "is this token valid?" on every request. That always gives the live answer, but it adds a network round trip from Render to Supabase to every request.

---

#### Round 2

Q4 (c) means deleting Guest User. I found a conflict that affects this round. In `docs/iterations/1/i01.d003-user-stories.md`:
- **US1, "Create a user with just my name"**, is marked Next.
- **US4, "Enter as the guest user"**, is marked Done.

#28 says Accounts are "created beforehand in Supabase", which means there's no sign-up in the app.

❓ **Q2** - **How Flask checks the token** (repeated now that (a) is explained): Should Flask check tokens locally with the cached public key?

➡️ Yes, (a).

---

❓ **Q8** - **What happens to US1 and US4**: #28 replaces both. Options:
- (a) Mark US1 as replaced by #28: Users come only from Accounts, and nobody can create one inside the app. Remove `POST /api/users` and its tests. Mark US4 as obsolete. Acceptance tests that need several identities put Users straight into the fake repository instead of calling the endpoint.
- (b) Keep US1 as an in-app sign-up flow: email, password and name.

➡️ Yes to (a). Sign-up contradicts "created beforehand" and adds scope to #28.

---

❓ **Q9** - **How a User is created for each Account**: Options:
- (a) A database trigger on `auth.users`: whenever an Account is created by any route (dashboard, script), a `users` row is inserted with the same ID. The name comes from the Account's `name` metadata, or from the part of the email before the `@` if there's no name.
- (b) A one-off script uses the Supabase admin API to create each Account and its `users` row together.
- (c) The team creates the Account in the dashboard, then runs a SQL `INSERT` for the User by hand.

➡️ Yes to (a). An Account can never exist without a User, so the 403 from Q3 becomes a "can't happen" safety net.

---

❓ **Q10** - **Database migration**: A new `003` migration that:
- deletes the pools whose creator or decider is Guest User (their picks are removed automatically);
- deletes the Guest User row;
- drops the `users.is_guest` column;
- adds a foreign key from `users.id` to `auth.users(id)` with `ON DELETE CASCADE`, so deleting an Account deletes its User;
- adds the trigger from Q9.

One catch: `pools.creator_id` has no cascade, so deleting an Account that owns pools would fail. For a demo that's acceptable; just delete those pools first.

➡️ Yes.

---

❓ **Q11** - **How the frontend gets the display name**: The header needs the User's name, which is stored in our `users` table, not in Supabase Auth. Options:
- (a) Add a Flask endpoint `GET /api/me` that returns `{id, name}` for the token's User. The root layout calls it once per request while someone is logged in.
- (b) Read the name from the Account metadata already inside the session.

➡️ Yes to (a). Flask stays the only code that reads app tables, and `/api/me` covers US5 "See who I am" as well.

---

❓ **Q12** - **Expired sessions and the protected route**:
- `hooks.server.ts` lets `@supabase/ssr` refresh the access token silently using the refresh token. If the refresh fails, the request is treated as logged out.
- Visiting `/pools/new` while logged out redirects to `/login?redirectTo=/pools/new`. After login, the user lands back there.
- If Flask returns 401 during a form submit (the token expired mid-flight), the user is sent to login the same way. The half-filled form is lost, which is acceptable for a demo.
- The "Create pool" link stays visible to logged-out visitors and leads to login.

➡️ Yes to all four.

### Alef (14:53)

> Is the meaning of Q2 (a) saved somewhere? For the conflicg of Q4 (c), #28 "accounts created beforehand in Supabase" means that we created an account (through a sign-up for example) and can restore those sessions. Q8 yes to (b), we'll add a an account creation flow to the app. If the language of #28 is unclear, we should change that, but the goal of #28 is to add authentication to the application including the creation of accounts. Q9 yes to (a). Q10 yes. Q11 yes to (a). Q12 yes to all four

### AI (14:54)

**Is Q2 (a) saved?** Not yet. It's only in this conversation so far. It's a good fit for an ADR (architecture decision record): it's a real trade-off (no per-request call to Supabase vs. a revoked token staying valid for up to an hour), and a later reader would reasonably ask "why not just call `get_user`?". If you confirm Q2 below, I'll write `docs/adr/0001-verify-supabase-tokens-locally.md` with the plain explanation from my last message in it.

**Sign-up:** that changes the shape of #28. People create their own Account in the app, a User is created automatically, and later visits restore the session. US1 becomes "Create an account". Round 3 covers the decisions that follow from that.

---

❓ **Q2** - **How Flask checks the token**: Check tokens inside Flask with Supabase's cached public key, and record the decision as ADR 0001?

➡️ Yes.

---

❓ **Q13** - **What the sign-up form asks for**: Email, password and display name. The name follows the existing US1 rules: trimmed, not blank, at most 80 characters. The SvelteKit action checks the name before calling Supabase, so the user gets a friendly error. The database also gets a `CHECK` rule as a backstop. Passwords use Supabase's default rule of at least 6 characters, and a duplicate email shows "An account with this email already exists."

➡️ Yes.

---

❓ **Q14** - **Email confirmation**: By default, Supabase makes new Accounts confirm their email before they can log in. Its built-in email sender only allows a few emails per hour, and that would get in the way of the two-account test on staging. Options:
- (a) Turn off "Confirm email" in the Supabase Auth settings. After sign-up you're logged in straight away.
- (b) Keep confirmation, and set up a custom email (SMTP) provider plus a "check your inbox" page.

➡️ Yes to (a). It's one switch in the Supabase dashboard, done by a person, and it goes on the list of staging setup steps.

---

❓ **Q15** - **Where sign-up runs**: The SvelteKit server calls `supabase.auth.signUp` with `{ name }` in the user metadata, which the Q9 trigger reads to create the User. Flask isn't involved. `POST /api/users` is still removed, because nothing in the app creates a User on its own any more. Acceptance tests that need a User put one straight into the fake repository.

➡️ Yes.

---

❓ **Q16** - **Updating the stories**: In #28's PR, update `i01.d003-user-stories.md` as follows:
- Rewrite **US1** as "Create an account", with new acceptance criteria: sign up with email, password and name; a blank or too-long name is rejected; a duplicate email is rejected; after sign-up I'm logged in and see my name.
- Mark **US4** "Enter as the guest user" as obsolete.
- Mark **US5** "See who I am" as delivered by #28.

➡️ Yes.

---

❓ **Q17** - **Rewording #28 on GitHub**: Edit the issue body (it's João's issue, so I'll show you the exact diff before posting anything):
- Replace "Use individual accounts and application profiles created beforehand in Supabase" with "Add account sign-up (email, password, display name); every new Account gets its User automatically. Restore sessions after reload and handle expired sessions."
- Add a line to the tasks: "Remove the shared Guest User and the pools that belong to it."
- Use the glossary words (Account, User, Pick) throughout.

➡️ Yes: draft the change here, then post it once you approve.

---

❓ **Q18** - **Changing the display name**: Can a User change their name after sign-up?

➡️ No, not in #28. Leave it for a later story.

### Alef (15:00)

> Yes to Q2. Yes to Q13. Yes to Q14, by I want to record this somewhere, because this is something we might want to change later, but I think for a demo it's ok going without email confirmation. Yes to Q15. Yes to Q16. Yes to Q17. Q18 not in #28, leave it for a later story

*[The AI wrote ADR 0001 and ADR 0002 and drafted the new body for #28.]*

### AI (15:01)

I've saved both decisions as ADRs:
- **`docs/adr/0001-verify-supabase-tokens-locally.md`** covers Q2. It includes the plain "stamped ID card" explanation, the alternatives we rejected, and what happens when an Account is revoked.
- **`docs/adr/0002-no-email-confirmation-for-the-demo.md`** covers Q14. It's marked accepted, explains why we skip confirmation, and says what turning it back on would take (an SMTP provider and a "check your inbox" page). It also notes the setting lives in the Supabase dashboard, not the code.

Q18 (renaming a User) will go into the stories doc as a new future story in #28's PR, as part of the Q16 edits.

##### Draft for the #28 issue (Q17), not posted yet

What changes:
- **Story:** "As a person joining the app, I want to create my own Account, sign in and see my name, so that the pools I create and the Picks I make belong to me."
- **Task 1:** "Add sign-up (email, password, display name), login, logout and the current User's name in the UI. Every new Account gets its User automatically."
- **Task 2:** loses the sentence "Use individual accounts and application profiles created beforehand in Supabase."
- **Task 3:** "…Remove the shared Guest User and the pools that belong to it."
- **Task 4:** "predictions" becomes "Picks".
- **Acceptance:** "each person can sign up, log in, reload, create their own pool and log out; frontend and backend consistently use the correct User."
- **New footer line:** "Terms (Account, User, Pick) follow `GLOSSARY.md`, added in this issue's PR."

The iteration backlog (`i01.d008`, section 1) has the same old wording. I'll update it in the PR together with the Q16 story edits.

---

#### Round 4

❓ **Q19** - **Post the #28 rewrite**: Run `gh issue edit 28` with the draft above?

➡️ Yes.

---

❓ **Q20** - **Database access rules**: This is a security gap that matters for "reject impersonation". After sign-up, `.env.example` comments that Flask should use the service_role key, but the committed value is a **publishable** key. Publishable keys are meant to be public: anyone who has it can call Supabase's REST API directly. If the app tables don't have row-level security (RLS) turned on, that person can insert a pool with any `creator_id` and skip Flask completely. Proposal:
- Turn on RLS for `users`, `pools`, `outcomes` and `picks` in migration 003, with no policies, so the public and logged-in roles are denied direct access.
- Flask uses the **secret** key, which bypasses RLS, so Flask's own access keeps working.
- Fix the `.env.example` comment and placeholder. Setting the real secret on Render is a manual step.

➡️ Yes.

---

❓ **Q21** - **One Supabase project for everything**: Local, staging and production all point at the same Supabase project (`xtaralttpdpluhkffryk`). That means migration 003 deletes the guest data everywhere, the Accounts you create on staging also exist in production, and ADR 0002's dashboard switch only has to be set once. Should we keep one shared project instead of creating a separate staging project?

➡️ Yes. For a demo it's the simplest option. I'll list it as a known limitation.

---

❓ **Q22** - **Backend error responses**: The backend's error rules:
- A protected route with no token, or with a forged, expired or wrong-audience token, returns **401** `{"error": "Authentication required."}`.
- A valid token whose User doesn't exist returns **403**.
- A body that includes `creator_id` returns **400** (from Q5).
- `GET /api/pools` stays public. `GET /api/me` and `POST /api/pools` require login.

➡️ Yes.

---

❓ **Q23** - **How backend tests produce tokens**: Options:
- (a) The test fixtures generate a throwaway ES256 key pair, sign real tokens with it, and give the matching public key to the verifier. The real checks then run in tests, so forged, expired and wrong-audience cases are tested for real.
- (b) Use a fake verifier that maps strings like `"token-ana"` to IDs. That's simpler, but the checks themselves go untested.

➡️ Yes to (a). User and pool repositories stay fake, as they are today.

---

❓ **Q24** - **Frontend testing**: The frontend has no test tooling at all: no Vitest, no Playwright. Options:
- (a) The backend acceptance tests carry the automated checks. The frontend flow gets a written manual checklist, run on staging with two Accounts: sign up, reload, create a pool, log out, log in as the second Account, expired-session redirect. That checklist is the definition-of-done evidence for the PR.
- (b) Add Playwright end-to-end tests now.

➡️ Yes to (a). Adding Playwright is a separate piece of work, which can become its own issue if the team wants it.

---

❓ **Q25** - **Header and logout**:
- When logged in, the header shows the User's name and a **Log out** button. The button is a POST form to `/logout`, which clears the session cookies and redirects to `/`.
- When logged out, the header shows **Log in** and **Sign up** links.
- `/login` and `/signup` link to each other.
- An already-logged-in person who opens `/login` or `/signup` is redirected to `/`.

➡️ Yes.

### Alef (15:09)

> Yes to Q19. Yes to Q20; is it worth recording? Yes to your suggestion on Q21. Yes to Q22. Q23 yes to (a). On Q24, why did you suggest (a) instead of adding playwright now? Yes to Q25

*[The AI posted the new body to #28 and wrote ADR 0003.]*

### AI (15:09)

I've posted the rewrite to #28 (Q19): https://github.com/MESW-LES-2627/les-project-group-8/issues/28

**Q20: yes, it's worth recording**, and I've written it as `docs/adr/0003-flask-is-the-only-door-to-app-tables.md`. It isn't hard to undo, but it passes the other two tests strongly:
- **It looks like a mistake.** RLS switched on with zero policies looks like unfinished setup. Someone could "fix" it by adding permissive policies or by pointing Flask at the publishable key, and either change quietly reopens the impersonation back door.
- **There was a real alternative.** Writing per-table RLS policies, rejected because it would split the business rules between SQL and Python.

**Q21:** the shared Supabase project will go into the "Not done yet" section of `docs/architecture.md` in the PR as a known limitation.

#### Q24: why I suggested (a) over Playwright

1. **The shared Supabase project (Q21) is the main blocker.** Playwright tests need a real backend and a real Supabase. Here, the only Supabase project is also production, so every test run would create real Accounts and pools in production data. That needs a cleanup routine, and if a run crashes halfway, the junk stays in production. A separate test project would fix this, but you just chose not to have one.
2. **Setup cost lands on #28.** The frontend has no test tooling at all. Playwright brings the package, browser binaries in CI, starting Flask and SvelteKit together in CI, and Supabase secrets in GitHub Actions. That's a sizable piece of infrastructure work hiding inside an auth issue.
3. **The parts most likely to break are already tested automatically.** Rejecting unauthenticated requests and impersonation attempts, the 401/403/400 rules, and ownership coming from the token are all backend behaviour, and Q23 covers them with real signed tokens. What the frontend adds is wiring (cookies, redirects, the header), and a manual check catches that well enough for a demo.
4. **The definition of done is already met.** It asks for "relevant automated tests" plus "verified on staging", and the checklist is the staging evidence.

**What (a) gives up:** session restore and the expired-session redirect are exactly the kind of thing that breaks silently later, and nothing automated would catch it. If that worries you, there's a middle ground: (c) a single Playwright smoke test (sign up → create a pool → log out) that runs **locally only**, not in CI, with a cleanup step. It's still most of the setup cost for one test, so I'd still choose (a) and open a separate issue for end-to-end testing, ideally with its own Supabase project.

---

❓ **Q24** - **Frontend testing** (repeated now that the reasoning is laid out): Manual staging checklist for #28, plus a new issue for Playwright end-to-end tests with a dedicated Supabase project?

➡️ Yes to (a), plus the follow-up issue.

---

That's the last open branch. Once you answer Q24, here's where everything stands:
- **Decisions:** Q1–Q25 are all settled.
- **Docs:** `GLOSSARY.md` and ADRs 0001–0003 are written.
- **GitHub:** #28 is updated.
- **Manual steps you'll need to do** (a `/wizard` script can walk you through them when we get there):
  - run migration 003;
  - turn off "Confirm email" in the Supabase Auth settings;
  - set the secret key on both Render services;
  - add the Supabase URL and publishable key to the frontend config and `wrangler.jsonc`.

Do you agree that we have a shared understanding? If so, the next step is `/to-spec`, run in this same session.

### Alef (15:14)

> Q24 yes to (a), and open a separate issue for end-to-end testing. I agree we have a shared understanding.

*[The AI read the issue-tracker conventions and opened #33.]*

### AI (15:14)

The grilling for #28 is done, and every decision is settled. I opened **#33** for Playwright end-to-end tests, labelled `needs-triage`: https://github.com/MESW-LES-2627/les-project-group-8/issues/33

The decisions are written down in these places:
- **`GLOSSARY.md`**: defines the terms Account, User and Pick.
- **`docs/adr/0001-verify-supabase-tokens-locally.md`**: Flask checks Supabase login tokens itself instead of asking Supabase on every request.
- **`docs/adr/0002-no-email-confirmation-for-the-demo.md`**: sign-up skips email confirmation.
- **`docs/adr/0003-flask-is-the-only-door-to-app-tables.md`**: the app tables block direct Supabase access, so only Flask can read or write them.
- **#28 on GitHub**: rewritten to include sign-up and to use the glossary terms.

These files aren't committed yet. They should go in #28's PR along with the code.

**Next step:** type `/mattpocock-skills:to-spec` in this session, without clearing. It turns these decisions into a spec, and after that `/mattpocock-skills:to-tickets` splits the spec into tickets.
