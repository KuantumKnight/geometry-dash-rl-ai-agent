# Media Archive

Media is recorded when it demonstrates a milestone, failure mode, or breakthrough that may be useful for a future project presentation. Every selected recording should be linked to the relevant commit and experiment notes.

The local `artifacts/` directory is intentionally gitignored because it contains generated frames and videos. Important recordings should be backed up separately before publishing or presentation work.

## Montage candidates

### `20260826T113120Z` — Environment state-flow demo

- Video: `artifacts/episodes/20260826T113120Z/episode.mp4`
- Duration: 20 seconds
- Capture: 60 FPS, 1,200 frames, 800×600 client area
- PNG evidence: 5 FPS samples plus `metadata.json`
- Shows: main menu → level info → attempt transition → gameplay → death animation/results → retry → gameplay
- Use: technical montage segment introducing why the environment needs state detection and reset control
- Status: keep as a montage candidate

## Supporting evidence

- `artifacts/reset_checks/20260826T114202Z/` — successful results-screen retry with before/after frames
- `artifacts/frames/20260826T115653Z_before.png` and `..._after.png` — direct jump-action evidence
- `artifacts/frames/20260826T120332Z_before.png` and `..._after.png` — no-op/results-screen capture evidence
- `tools/stress_reset.py` — 50-death reset reliability run; its summary is recorded in `docs/learning-log.md`

## Archive rule

For each future episode, keep the MP4 and metadata when it shows a new capability, a meaningful failure, or a measurable breakthrough. Record its UTC timestamp, duration, FPS, resolution, relevant commit, and intended presentation use here. Routine benchmark output stays in the learning log unless it produces a milestone worth showing visually.
