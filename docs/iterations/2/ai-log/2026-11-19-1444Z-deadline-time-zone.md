# A Pool's deadline is read in the User's time zone

- **Who:** Alef Keuffer.
- **Tools:** Claude Code 2.1.311 (Claude Opus 5.5), `implement`, `tdd` and
  `code-review` skills from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills),
  Playwright 1.65.1.
- **Outcome:** a fix for
  [#129](https://github.com/MESW-LES-2627/les-project-group-8/issues/129),
  stacked on #124's branch.
- **Delegated:** the whole change. The server's `validatePool` now rejects a
  deadline without a zone (unit test first). `PoolForm.svelte` rewrites the
  posted `deadline` to UTC ISO with `localInputToIso` in a `formdata` listener.
  `pools.spec.ts` runs in `Asia/Kolkata` and expects exactly `07:00 UTC`. The
  review ran as two sub-agents (standards, spec).
- **Where it was wrong:** the first version kept the visible input in `$state`
  and posted a hidden input. Filling the deadline then cleared the Name field,
  so the form never submitted: Svelte's compiled template set Name's `value`
  again in the same effect. A field-value log in the e2e test found it, and the
  `formdata` listener, which has no reactive state, replaced it.
- **How we checked:** `pnpm check`, `pnpm test` (36) and `pnpm test:e2e` (10)
  pass.
- **Notes:** without JavaScript the form posts the zoneless local time, and the
  server now rejects it ("Deadline must include a time zone."), where before
  it saved the Pool in the server's zone. The zone check accepts `Z` and
  `±HH:MM`, not `±HHMM`, which the form never sends.
