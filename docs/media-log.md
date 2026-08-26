# Media Evidence Log

This is the catalog of footage that actually exists. The planned story, required shots, capture standards, metadata schema, and publishing rules live in [`montage-plan.md`](montage-plan.md).

Raw frames and videos remain under the gitignored `artifacts/` directory. A clip is not safely preserved until it has a checksum and a second backup.

## Status legend

- **RAW ONLY** — captured locally but not reviewed or backed up.
- **CANDIDATE** — useful for the story; metadata or backup may still be incomplete.
- **SELECTED** — approved for an edit and linked to its evidence.
- **PUBLISHED** — optimized asset is available at a durable public link.
- **REJECTED** — intentionally excluded; retain only if required for experiment evidence.

## Existing montage candidates

### M05 / `20260826T113120Z` — Environment state-flow demo

| Field | Value |
| --- | --- |
| Status | **CANDIDATE** |
| Local source | `artifacts/episodes/20260826T113120Z/episode.mp4` |
| File size | 1,082,879 bytes |
| Duration | 20 seconds |
| Capture | 60 FPS measured, 1,200 frames, 800×600 client area |
| Supporting files | 5 FPS PNG samples and `metadata.json` |
| Shows | Main menu → level info → attempt transition → gameplay → death/results → retry → gameplay |
| Intended use | Explain why the environment needs state detection and reset control |
| Related learning | Environment/episode semantics in `learning-log.md` |
| Git commit | Not yet recorded in sidecar metadata |
| SHA-256 | `DDF0BFFA5B924B75238D9FDA7373BCC874E3133D5FC7BCD8C0FC294664EF48E9` |
| Second backup | `media-backups/20260826T113120Z/episode.mp4` (local ignored backup; hash matches source) |
| Privacy review | Pending |
| Rights review | Pending |

#### Required preservation work

- [x] Compute and record the source-video SHA-256.
- [ ] Record the exact related commit or nearest historical commit.
- [x] Copy the source video to `media-backups/20260826T113120Z/` outside `artifacts/`; metadata and selected PNG evidence remain pending.
- [ ] Restore/open the backup copy once.
- [ ] Review the full frame for personal paths, usernames, notifications, or unrelated windows.
- [ ] Create a short review proxy without modifying the raw source.

## Supporting still evidence

| Evidence | What it proves | Montage use | Status |
| --- | --- | --- | --- |
| `artifacts/reset_checks/20260826T114202Z/` | Results-screen retry succeeded | Possible M06 insert | RAW ONLY |
| `artifacts/frames/20260826T115653Z_before.png` and `..._after.png` | Jump input visibly changed the game | Possible M04 before/after | RAW ONLY |
| `artifacts/frames/20260826T120332Z_before.png` and `..._after.png` | No-op/results-screen capture evidence | Technical supporting material | RAW ONLY |
| `tools/stress_reset.py` plus `learning-log.md` result | 50 consecutive recorded deaths/resets, zero recorded reset failures | M06 counter/graphic source | Evidence exists; video not selected |

## Next capture queue

These are the highest-value shots to capture next; see the full M00–M22 list in the montage plan.

- [ ] **M00 — Project origin:** a short honest snapshot of the game, current repository, and learning goal.
- [ ] **M01 — Human reference:** one clean human attempt on the target level.
- [ ] **M02 — Locked baselines:** matched no-op, random, and periodic policy clips.
- [ ] **M03 — Observation pipeline:** raw frame beside transformed observations/frame stack.
- [ ] **M04 — Controlled jump:** action indicator synchronized with the first verified jump.
- [ ] **M07 — Detector failure/fix:** preserve the next meaningful real detector bug before fixing it.
- [ ] **M08 — Progress/reward overlay:** raw progress, filtered delta, and reward components.
- [ ] **M09 — Learning proof:** short clips of hand calculations, toy implementations, and reflections.

## New-candidate entry template

Copy this section when a recording becomes a candidate.

```md
### [Shot ID] / [capture ID] — [Short title]

| Field | Value |
| --- | --- |
| Status | RAW ONLY / CANDIDATE / SELECTED / PUBLISHED / REJECTED |
| Local source | `artifacts/...` |
| Duration | |
| Capture | requested FPS, measured FPS, frames, resolution |
| Shows | |
| Intended use | |
| Learning note | |
| Experiment/run | |
| Git commit | |
| Checkpoint/seed | |
| Protocol/contracts | |
| SHA-256 | |
| Second backup | |
| Privacy review | pending/passed |
| Rights review | pending/passed |
| Published link | |

Notes: [Why this clip matters, known problems, preferred in/out points.]
```

## Archive rule

Keep footage when it demonstrates a new capability, a meaningful failure, a learning breakthrough, a measurable policy improvement, or an irreplaceable first. Routine recordings can be deleted only after experiment-retention needs are met. Every selected clip must link to its commit, configuration/run, learning note, checksum, backup, and intended montage shot.
