# Stop ffmpeg eating the story gallery's file list

- **Who:** Alef Keuffer.
- **Tools:** Claude Code (Claude Opus 5.5).
- **Outcome:** `.github/workflows/stories.yml` runs ffmpeg with `-nostdin`, so the Publish step no longer fails with `Error opening input file stories/S3 See the pools.webm`.
- **Delegated:** Read the failed run's log ([job 140059364084](https://github.com/MESW-LES-2627/les-project-group-8/actions/runs/45863228196/job/140059364084)). Found that ffmpeg, run inside a `while read` loop, read the loop's stdin and swallowed the first bytes of the next file name (`US3 …` became `S3 …`). Wrote the one-flag fix.
- **How we checked:** Reproduced locally with four 15-second test videos through the same loop. Without `-nostdin`, a later name lost its `US` prefix and ffmpeg failed. With it, all four GIFs were made.
