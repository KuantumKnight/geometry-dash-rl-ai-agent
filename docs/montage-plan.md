# Montage Capture Plan

The final montage should show a story, not a random collection of successful runs:

> A person learns reinforcement learning by first building a trustworthy game environment, then teaching an agent, measuring whether it truly improves, and documenting the failures along the way.

## The three rules

1. **Capture milestones when they happen.** A genuine first success or surprising failure is hard to recreate later.
2. **Preserve evidence, not only pretty footage.** Every technical clip must link to a commit, config, run, checkpoint, or learning note.
3. **Keep raw material separate from the edit.** Record clean game footage and synchronized telemetry; add crops, labels, speed ramps, and music only in derived edit files.

## Final story outline

Target a 45–90 second main montage and retain enough material for a 3–5 minute technical walkthrough.

1. **The challenge:** Geometry Dash gameplay and the goal of learning RL through it.
2. **Before learning:** no-op/random/periodic baselines fail early.
3. **Building the senses:** capture, observations, screen states, and progress detection.
4. **Building control:** jump actions, death detection, and reliable automatic reset.
5. **Learning the ideas:** quick glimpses of hand calculations, toy agents, notes, and experiments.
6. **The first signs of learning:** checkpoint behavior improves over time.
7. **The result:** locked baseline versus held-out trained-agent evaluation.
8. **Honest ending:** limitation/failure plus the next research question.

## Must-capture shot list

Capture the shots when their trigger occurs. Do not mark a shot complete until the source and metadata are backed up.

| ID | Shot | Trigger | What must be visible | Learning/story purpose |
| --- | --- | --- | --- | --- |
| M00 | Project origin | Now | Game, empty/early repo state, and one sentence of the goal | Establishes where the journey began |
| M01 | Human reference | Before serious training | A short clean human attempt on the target level | Shows the task and timing challenge |
| M02 | No-op/random/periodic baseline | Locked baseline evaluation | Same layout and protocol for each policy | Proves improvement has a comparison point |
| M03 | Pixels become observations | Observation pipeline milestone | Raw frame beside crop/resize/grayscale/stack views | Explains what the agent actually sees |
| M04 | First controlled jump | Action verification | Action indicator synchronized with the visible jump | Shows perception-to-action control |
| M05 | Screen-state machine | State detector qualification | State label changing through intro, gameplay, death, results, reset | Explains episode boundaries |
| M06 | Reset reliability | 50/100-reset qualification | Rapid sequence/counter of automatic deaths and resets | Shows engineering reliability |
| M07 | Detector failure and fix | First meaningful detector bug | Failure frame, wrong label, corrected behavior | Demonstrates debugging and honesty |
| M08 | Progress and reward overlay | Reward contract qualification | Progress, progress delta, reward components, and state | Makes reward design understandable |
| M09 | Learning by hand | Each key RL module | Hand calculation/diagram plus the matching test or toy output | Proves the creator learned the theory |
| M10 | Toy agent learns | Tabular/DQN/PPO sanity task | Learning curve and behavior before/after | Shows algorithm understanding before the game |
| M11 | First live training update | First correct live smoke test | Environment, action, reward, loss/step counter | Marks the start of real learning |
| M12 | First measurable improvement | Agent first beats baseline threshold | Checkpoint ID, protocol, progress, and comparison | Preserve this immediately; it cannot be staged honestly later |
| M13 | Checkpoint evolution | At fixed training steps | Same obstacle/conditions across early, middle, late checkpoints | Visually communicates learning over time |
| M14 | Repeated failure location | During diagnosis | Several attempts failing at the same obstacle | Sets up a scientific iteration story |
| M15 | Hypothesis → fix → outcome | After a controlled improvement | Before/after with the one changed factor labeled | Shows experimental reasoning |
| M16 | Milestone progress | First 25%, 50%, 75%, and best run | Percentage, checkpoint, seed, and evaluation/training label | Creates a progression sequence |
| M17 | First legitimate completion | First completion under declared conditions | Entire final section, completion state, run metadata | Preserve raw footage and ring buffer immediately |
| M18 | Baseline versus trained agent | Final held-out evaluation | Side-by-side or matched cuts under the same protocol | Main result shot |
| M19 | Robustness/generalization | First held-out condition | New condition label and outcome | Shows whether behavior is robust or memorized |
| M20 | Honest limitation | Final evaluation | Representative failure, not a cherry-picked glitch | Keeps claims credible |
| M21 | Creator teach-back | Final documentation stage | Short explanation of state, action, reward, algorithm, result | Proves personal understanding |
| M22 | Closing hero shot | Release | Best verified evaluation clip with minimal readable overlay | Final montage ending |

## Capture triggers that should never be postponed

- [ ] First action that visibly affects the game.
- [ ] First reliable automatic reset loop.
- [ ] First detector failure that teaches something important.
- [ ] First correct progress/reward trace.
- [ ] First successful toy RL learning curve.
- [ ] First live model update without pipeline errors.
- [ ] First checkpoint that beats the locked baseline criterion.
- [ ] First 25%, 50%, 75%, and 100%/completion milestone.
- [ ] First failure that leads to a successful controlled fix.
- [ ] Final baseline and trained-agent evaluations under identical conditions.

For training milestones, keep a rolling pre-event buffer if practical. Otherwise, save frequent evaluation recordings so an unexpected first success is not lost.

## Raw capture standard

### Video

- Capture the complete game client without stretching or hiding relevant UI.
- Prefer 60 FPS when the machine can sustain it; store measured FPS, not only requested FPS.
- Preserve the original game-client resolution and aspect ratio.
- Capture 5–10 seconds before and after the key event when possible.
- Use a broadly playable proxy such as H.264 with `yuv420p` for review; preserve the highest-quality practical source separately.
- Do not bake music, subtitles, speed changes, zooms, or decorative overlays into the only copy.
- Record microphone narration separately when possible so it can be rewritten.
- Avoid copyrighted music in repository/demo assets.

### Synchronized technical data

Where relevant, store timestamps for:

- requested and dispatched action;
- observation/frame ID;
- screen state and confidence;
- raw/filtered progress;
- reward components;
- terminated/truncated reason;
- policy probability/Q-values when meaningful;
- environment step and episode;
- checkpoint and run ID.

The overlay shown in an edited clip must be reproducible from saved telemetry, not typed from memory.

### Framing for the final edit

- Keep important content inside a center-safe area suitable for a 16:9 edit.
- Never stretch the 4:3 game capture. Place it on a designed canvas or crop only when the crop does not alter the evidence.
- Leave room beside the game for labels, graphs, code, or a state/reward panel.
- Capture clean versions with and without diagnostic overlays.
- Prefer short readable labels over dense dashboards.

## Sidecar metadata required for every selected clip

Store a JSON sidecar beside the raw clip and summarize it in [`media-log.md`](media-log.md).

```json
{
  "shot_id": "M12",
  "capture_id": "YYYYMMDDTHHMMSSZ-short-name",
  "recorded_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "source_file": "episode.mp4",
  "duration_seconds": 0,
  "requested_fps": 60,
  "measured_fps": 0,
  "resolution": [800, 600],
  "git_sha": "",
  "dirty_tree": false,
  "experiment_id": "",
  "run_id": "",
  "checkpoint_id": "",
  "seed": null,
  "environment_version": "",
  "observation_version": "",
  "reward_version": "",
  "protocol_id": "",
  "level": "Stereo Madness",
  "mode": "cube",
  "start_progress": null,
  "end_progress": null,
  "outcome": "",
  "learning_note": "",
  "intended_use": "",
  "sha256": "",
  "privacy_reviewed": false,
  "rights_reviewed": false,
  "backup_locations": []
}
```

Use `null` for information that truly does not apply. Do not invent missing values.

## Archive layout

Continue to preserve the existing `artifacts/episodes/` material. For new selected media, use a structure that separates source, telemetry, and edit outputs:

```text
artifacts/media/
├── raw/<capture-id>/
│   ├── source.mp4
│   ├── metadata.json
│   ├── telemetry.jsonl
│   └── notes.md
├── proxies/<capture-id>.mp4
├── selects/<shot-id>/<capture-id>.mp4
└── exports/<montage-version>/
```

Do not reorganize or delete existing artifacts merely to match this layout. Migrate only after checksums and backups exist.

### Backup rule

Every irreplaceable selected clip must have:

- the working copy;
- one backup on a different device or reliable storage service;
- a SHA-256 checksum recorded in metadata;
- a restore test for at least one sample asset;
- no secrets, unrelated desktop content, or private notifications.

## Selection rubric

Score each candidate from 0–2 on the following dimensions:

- **Story:** does it advance the narrative?
- **Evidence:** is it tied to a real run/commit/checkpoint?
- **Clarity:** can a new viewer understand what changed?
- **Uniqueness:** would this moment be difficult to recreate?
- **Visual quality:** is the action readable and capture stable?
- **Honesty:** does it show the actual protocol without misleading edits?

Keep high-scoring shots, mark uncertain shots as alternates, and discard routine footage after retention needs are met.

## GitHub publishing strategy

- Keep raw video, frame dumps, and checkpoints out of normal git history.
- Commit the media catalog, metadata schema, checksums, thumbnails, and small optimized assets only.
- Use GitHub Releases or another durable artifact host for selected downloadable videos/checkpoints.
- Use Git LFS only after intentionally accepting its bandwidth/storage trade-offs.
- Link every published clip to the experiment report or learning module it supports.
- Label training footage and held-out evaluation footage clearly.
- Do not distribute the game executable or extracted game asset packs.
- Add non-affiliation and game-ownership language to the README and release.

## Edit integrity checklist

- [ ] Speed changes are labeled when they could affect perceived skill or timing.
- [ ] Baseline and trained-agent comparisons use the same crop, speed, and protocol.
- [ ] Progress/reward numbers come from saved telemetry.
- [ ] Training clips are never presented as held-out evaluation.
- [ ] Failed seeds/runs are not hidden from the written result.
- [ ] Audio and visual assets have known rights.
- [ ] Personal paths, usernames, notifications, and unrelated windows are removed.
- [ ] Captions and alt text communicate the important result without sound.
- [ ] The final export is tested on desktop, mobile, and GitHub playback.

## Existing candidate

The current `20260826T113120Z` state-flow recording is a useful M05 candidate. It shows main menu → level info → attempt intro → gameplay → death/results → retry → gameplay at a measured 60 FPS. Preserve and checksum it before changing the artifact layout.
