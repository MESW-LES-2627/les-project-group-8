# Stop Supabase's ports clashing with the runner's ephemeral ports

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5).
- **Outcome:** PR [#220](https://github.com/MESW-LES-2627/les-project-group-8/pull/220): the `screenshots` and `e2e` workflows reserve ports 54320-54329 before anything else runs, and the screenshots workflow no longer hides a failed Supabase start behind `Cannot find module './results.json'`.
- **Delegated:** Read the failed run's log and found `failed to bind host port 0.0.0.0:54322/tcp: address already in use` in both capture steps. Proposed that an outbound connection had taken 54322 from Linux's ephemeral range (32768-60999). Reproduced it on a GitHub runner from a throwaway branch, then wrote the fix.
- **What we decided ourselves, and why:** Asked for the cause to be confirmed before any fix went in.
- **Where it was wrong:** It first proposed moving the whole ephemeral range. It switched to `ip_local_reserved_ports`, which reserves only Supabase's ports and is the kernel setting meant for this. Its first reproduction ran both cases on one runner, so the second case failed because of the first case's leftover socket. It reran that case alone.
- **How we checked:** The throwaway workflow pinned the ephemeral range to 54322 and opened one outbound connection. `docker run -p 54322:80` then failed with the same error as CI. On a fresh runner with 54320-54329 reserved, the outbound connection took 54330 and the publish succeeded. Checked locally that the `results.json` guard exits 1 when the file is missing.
