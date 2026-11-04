---
status: accepted
---

# Sign-up does not confirm the email address

"Confirm email" is turned off in the Supabase Auth settings, so a person who signs up is logged in straight away and nobody proves they own the address. Supabase's built-in mailer only sends a handful of emails per hour, which would block testing sign-up with several Accounts on staging, and setting up our own SMTP provider plus a "check your inbox" flow is not worth it for a class demo.

## Consequences

- Anyone can sign up with an address they don't own, and there is no password-reset-by-email path we can rely on.
- The switch lives in the Supabase dashboard, not in the code: it must be set by hand on every Supabase project we use, and it is the first thing to revisit if the app is ever used beyond the demo. Turning it back on needs a custom SMTP provider and a "check your inbox" page after sign-up.
