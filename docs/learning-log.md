# Learning Log

This is the running journal for the project. Each entry should explain what changed, what was learned, and what will be tested next.

## 2026-08-26 — Project foundation

### Context

The project is a personal exploration of reinforcement learning through a Geometry Dash agent.

### Decisions

- Start by validating the interaction loop before selecting an RL algorithm.
- Treat the repository as both the implementation and the learning record.
- Keep the local Geometry Dash installation outside version control.

### Initial hypothesis

The first technical risk is not the choice of algorithm. It is whether the agent can repeatedly observe the game, send an action, detect failure, and reset the level reliably.

### Next experiment

Build the smallest possible interaction prototype: capture one frame, send one jump or no-op action, and verify a reliable termination signal.

## 2026-08-26 — Capture/action prototype scaffold

### What changed

- Added `tools/capture_action.py`.
- Added Pillow as the first dependency for screen capture.
- Added an explicit `--action jump` flag; the default is a no-op.
- Kept game launching manual so the prototype cannot unexpectedly start the game.

### Current limitation

The first draft captured the primary display, which was too broad for an RL observation. The prototype now locates the visible window owned by `GeometryDash.exe`, focuses it, and captures only its client area. Game-state detection is still not implemented.

### Next test

Start Geometry Dash manually, run the prototype with `--action noop`, and inspect the two game-window frames. Only then test `--action jump`.

## 2026-08-26 — Window lookup bug

### Failure

The first focused-window test reported that no Geometry Dash window was found even though the process was running.

### Root cause

The game window was minimized. The lookup rejected minimized windows before the restore step could run.

### Fix

Allow visible minimized windows to match the executable path, then restore and focus the matching window before calculating its client-area bounds.

## 2026-08-26 — DPI coordinate mismatch

### Failure

The script found the window and reported the expected client size, but captures still included the terminal and title bar.

### Root cause

Windows desktop scaling was 150%. Win32 returned logical window coordinates while Pillow captured physical screen pixels.

### Fix

Make the capture process per-monitor DPI aware before querying window coordinates so Win32 and Pillow use the same coordinate system.

## 2026-08-26 — Jump action validated

### Result

The focused-window prototype successfully delivered a jump action inside a playable level. This validates the first action in the environment: a space-bar press can be sent to Geometry Dash without launching or controlling another window.

### Next experiment

Record a short gameplay trace containing an alive-to-dead transition. Inspecting those frames will determine the first reliable death-state signal and the reset action.

## 2026-08-26 — Episode video recording

### Decision

Each recorded episode will keep both PNG frames and a local MP4 video. The MP4 is easier to review and document, while the individual frames remain useful for state detection and future RL observations.

### Repository policy

Episode artifacts stay outside Git history because raw frames and videos can become large. Commit metadata, findings, and selected summaries; keep videos locally or attach selected milestone clips to GitHub Releases later.

## 2026-08-26 — Target 60 FPS pixel observations

### Decision

New episode recordings will target 60 FPS. The earlier 5 FPS setting was useful for debugging the capture path, but it is too sparse for fast Geometry Dash collisions and jump timing.

### Important distinction

The recorder captures pixels at the game rate, but the eventual RL policy does not have to make a new decision every frame. We can preserve 60 FPS observations while using frame-skip or action-repeat to control training cost after measuring the environment.

### Measurement rule

The recorder now stores both requested and measured FPS and uses the measured rate when encoding the video. This prevents a slow capture loop from creating a video that plays faster than the real episode.

### Implementation note

The recorder uses a fast screen-grab backend for the 60 FPS video stream and saves lower-rate PNG samples by default. Use `--png-fps 60` when every frame is needed for an experiment; otherwise the video remains the complete pixel observation record while the samples support quick inspection.

## 2026-08-26 — Baseline death detection

### Evidence

The clean episode `20260826T111858Z` contains gameplay frames followed by the static death/results overlay. The overlay has a dark central panel and bright green result controls; gameplay and the death animation do not share both properties.

### Implementation

Added `tools/game_state.py` with a normalized pixel heuristic and `tools/scan_episode.py` for offline transition checks. The detector currently identifies a frame as `dead/results` when the lower-center green ratio is above `0.04` and the center dark ratio is above `0.50`.

### Limitation

This is a baseline calibrated on one clean episode, not a final general detector. It must be tested across more levels, window sizes, and death animations before being used inside a training environment.

## 2026-08-26 — Full screen-state map

### Result

The latest 20-second episode contains the complete control flow from main menu to level selection, attempt transition, gameplay, death animation, results, retry transition, and a second gameplay segment.

### Design consequence

Only `GAMEPLAY` should be exposed as a learning observation. Menu, level-info, attempt-intro, death-animation, and results screens belong to the environment controller and should not be mixed into the policy’s training data.

See [screen-state-map.md](screen-state-map.md) for the sampled frame ranges and proposed state flow.

## 2026-08-26 — Guarded reset controller

### Implementation

Added `tools/reset_episode.py`. It only sends `R` after the current frame is classified as `RESULTS`, waits for the results overlay to clear, and saves before/after verification frames.

### Not yet validated

The controller has passed static checks but still needs a live test from a real results screen. The reset checklist remains open until the after-reset frame is confirmed as the next attempt and subsequent gameplay.

### Layout bug found

The first live test used an `800×600` game window. The results controls were lower than in the original `1359×768` calibration episode, so the detector looked at the wrong vertical region. The lower-green feature region was widened and made resolution-normalized before retrying the live reset.

### Input finding

On this Geometry Dash build, neither `R` nor Space cleared the results screen. The retry control must be clicked. The reset controller now clicks the normalized lower-left retry position after the `RESULTS` guard passes.

### Live validation

The reset controller successfully detected a real results screen, clicked retry, and produced an `after_reset.png` frame showing gameplay in Attempt 6. Reset is now validated for this window layout.

## 2026-08-26 — Initial pixel environment API

### Implementation

Added `GeometryDashEnv` with `reset()` and `step(action)`, two discrete actions, `160×90` RGB pixel observations, and a provisional terminal penalty.

### Scope

This wrapper proves the basic environment shape only. It does not yet include a progress reward, time limit, robust gameplay-state classification, or a learning algorithm.

## 2026-08-26 — Temporal environment controls

### Implementation

Added configurable `frame_skip` and `max_steps`. The default environment captures at 60 FPS, repeats each action for four frames, and truncates an episode after 900 decisions.

### Reasoning

This separates visual capture rate from policy decision rate. The agent can later make decisions at roughly 15 Hz while preserving the game’s 60 FPS timing for action effects and video evidence.

## 2026-08-26 — Terminal progress reward

### Implementation

Added a results-screen progress-bar estimator. A terminated episode now receives `-1 + progress_ratio`, where `progress_ratio` is the detected normal-mode bar fill from `0.0` to `1.0`.

### Reasoning

This gives the agent a meaningful distinction between dying at 1% and dying at 50% without pretending that raw screen motion is progress. The next improvement is to validate this estimator across more levels and add continuous progress tracking if the game exposes a reliable signal during gameplay.

## 2026-08-26 — Removed per-action focus latency

### Implementation

Changed the input path so `reset()`/`_ensure_window()` focuses Geometry Dash once, while `send_key()` only sends the key event. Reduced the Space key hold from 50 ms to 5 ms.

### Reasoning

Focusing before every jump added roughly 250 ms of avoidable latency. With `frame_skip=4` at 60 FPS, the target is now approximately 15 environment decisions per second instead of paying the focus delay on every action. PPO/DQN work is intentionally still deferred.

### Next measurement

The next milestone is a repeatable environment smoke test of about 100 random actions, measuring step time, decision rate, and failures. The interaction change must first be confirmed by a live jump test.

### Live validation

The direct jump command completed successfully. A controlled environment check then returned a `(90, 160, 3)` observation from `reset()` and completed `step(1)` across four frames with `terminated=False` and `truncated=False`. One sample took about 194 ms; this is only a sanity check, not the final throughput result.

## 2026-08-26 — Added the 100-step environment benchmark

### Implementation

Added `tools/benchmark_env.py`. It resets the environment, chooses random no-op/jump actions, measures each `env.step()` with `time.perf_counter()`, resets after deaths or truncations, and reports mean, median, minimum, maximum, decisions per second, deaths, and resets.

### Reasoning

This measures the real distribution of environment-step times before changing any capture, timing, or input code. The benchmark is intentionally not an optimization and does not start PPO or DQN.

### First measurement

Command: `py -3.13 tools\\benchmark_env.py --seed 42`

The first run reached step 21 but stopped when an automatic reset timed out. After manually confirming that the existing reset controller could recover the results screen, the unchanged benchmark completed all 100 steps:

```text
steps:             100
mean step time:    165.23 ms
median step time:  167.76 ms
min:               45.21 ms
max:               184.07 ms
decisions/sec:     6.05
deaths:            6
resets:            7
```

This is the baseline measurement only. It shows that the current loop is slower than the initial 15 decisions/second target, while the first failed run also shows that reset reliability needs separate investigation. No optimization was made based on this result.

## 2026-08-26 — Added component profiler

### Implementation

Added `tools/profile_env_step.py` to measure the existing per-frame sequence separately: the frame-rate sleep, MSS capture, `is_death_screen()` detection, and observation conversion. It also reports total frame time and unaccounted measurement overhead.

### Scope

This is profiling only. The detector, capture path, timing, and reset behavior were not replaced or optimized. The profiler uses the current environment methods and a fixed optional seed so the measurements can be repeated before changing code.

### First profile

Command: `py -3.13 tools\\profile_env_step.py --seed 42`

The 100-frame profile completed with one detected death and two total resets:

```text
frames:             100
mean sleep:         17.00 ms
mean capture:       15.16 ms
mean death detect:  9.32 ms
mean observation:   2.05 ms
mean frame total:   43.53 ms
unaccounted:        0.01 ms
deaths:             1
resets:             2
```

The result explains the earlier roughly 168 ms decision time: four profiled frames total about 174 ms. The current detector is measurable at roughly 9 ms per frame, and capture is roughly 15 ms per frame. These are observations only; no optimization has been made yet.

## 2026-08-26 — Vectorized death detector with NumPy

### Implementation

Replaced the Python pixel loops in `death_screen_features()` with NumPy masks and region means. The `is_death_screen()` thresholds were left unchanged. Capture, frame timing, reward, reset, and RL code were not modified.

### Post-change measurements

Component profile command: `py -3.13 tools\\profile_env_step.py --seed 42`

```text
frames:             100
mean sleep:         17.01 ms
mean capture:       47.68 ms
mean death detect:  11.27 ms
mean observation:   4.98 ms
mean frame total:   80.94 ms
unaccounted:        0.01 ms
deaths:             0
resets:             1
```

Environment benchmark command: `py -3.13 tools\\benchmark_env.py --seed 42`

```text
steps:             100
mean step time:    127.00 ms
median step time:  129.56 ms
min:               35.49 ms
max:               148.19 ms
decisions/sec:     7.87
deaths:            4
resets:            5
```

The complete benchmark improved from 165.23 ms to 127.00 ms mean step time. However, this profile run measured death detection at 11.27 ms versus the earlier 9.32 ms baseline, while capture and observation timings also changed substantially. The measurements are recorded as-is; no causal performance claim is made yet.

### Correctness check

Compared the vectorized feature values with the previous pixel-loop calculation across 407 saved frames: maximum feature difference was `0.000000000000`, with zero mismatches.

## 2026-08-26 — Added offline detector benchmark

### Implementation

Added `tools/benchmark_detector_offline.py`, which compares the old pixel-loop implementation with the current NumPy implementation on saved PNG frames. Image loading is outside the timed sections; Geometry Dash, MSS capture, sleeping, reset, and the environment are not involved.

### Scope

The benchmark runs multiple alternating timed passes per frame and checks feature equivalence at the same time. This isolates whether vectorization made the detector itself faster before changing frame pacing.

### Offline result

Command: `py -3.13 tools\\benchmark_detector_offline.py --repeats 5`

```text
frames:             407
repeats:            5
old mean/frame:     10.3118 ms
new mean/frame:     4.7971 ms
speedup:            2.15x
old/new mismatches: 0
max feature diff:   0.000000000000
```

The NumPy implementation is 2.15× faster in the isolated detector benchmark. The earlier live profile was noisy because capture and other live components varied substantially; frame pacing remains a separate, future change.

## 2026-08-26 — Added deadline-based frame pacing

### Implementation

Replaced the fixed `sleep(1 / fps)` inside `step()` with a monotonic deadline schedule. Each frame waits only until its target deadline; capture and detection time are allowed to consume the interval without adding a second full sleep.

### Benchmark

With `frame_skip=4`, `fps=60`, and random actions using seed 42:

```text
steps:             100
mean step time:    86.87 ms
median step time:  86.65 ms
min:               69.21 ms
max:               103.77 ms
decisions/sec:     11.51
deaths:            1
resets:            2
```

This improved the live baseline from 127.00 ms / 7.87 decisions/sec to 86.87 ms / 11.51 decisions/sec. The environment is now close to the initial 12–15 decisions/sec target; reset and capture reliability remain unfinished Phase 1 work.

## 2026-08-26 — Made reset state-aware and deterministic

### Implementation

Added coarse screen-state classification for results, level/transition screens, main menu, and unknown screens. `reset()` now refreshes focus, clicks retry only after a results screen is detected, tolerates the transition interval, requires consecutive level-like frames, and fails explicitly on the main menu or unknown screens. Key input restores focus only when Geometry Dash actually lost foreground focus.

Added `tools/stress_reset.py` for unattended no-op episodes and reset-failure counting.

### Stress test

Command: `py -3.13 -u tools\\stress_reset.py --deaths 50`

```text
target deaths:     50
deaths reached:    50
reset attempts:    50
reset failures:    0
episode failures:  0
```

The reset path completed 50 consecutive deaths and retries without a failure. Accidental menu/unknown screens are now detected and reported instead of being silently accepted as valid gameplay.

## 2026-08-26 — Refreshed capture bounds during episodes

### Implementation

`_capture()` now refreshes the Geometry Dash client rectangle before every MSS grab and replaces the cached bounding box when the window moves or resizes. Reset already refreshes the window handle and bounds through `_ensure_window()`. The current bbox is also returned in `reset()` and `step()` info for diagnostics.

Added `tools/verify_capture_stability.py` to check repeated captures, image sizes, and tracked bounding boxes.

### Stability check

Command: `py -3.13 tools\\verify_capture_stability.py --samples 100`

```text
samples:             100
unique bounding boxes: 1
unique image sizes:   1
first bbox:           (63, 488, 863, 1088)
last bbox:            (63, 488, 863, 1088)
first image size:     (800, 600)
last image size:      (800, 600)
```

The live window remained stable for 100 captures, and the implementation now detects movement or resize on the next capture instead of continuing with stale coordinates.

## 2026-08-26 — Added Gymnasium spaces and base class

### Implementation

Added `gymnasium.Env` inheritance, `Discrete(2)` for no-op/jump actions, and a `Box` observation space matching the returned `(90, 160, 3)` `uint8` pixels. `reset(seed=None, options=None)` now follows the standard Gymnasium signature.

### Scope

This commit only cleans up the environment API. It does not introduce an agent, training loop, or reward changes.

## 2026-08-26 — Added environment contract tests

### Coverage

Added a standard-library `unittest` suite covering reset smoke behavior, main-menu rejection, jump dispatch, results-screen detection, terminal progress reward, deadline pacing, action/observation spaces, and bbox refresh after a simulated window move.

### Result

```text
Ran 9 tests in 0.020s
OK
```

The unit tests run without Geometry Dash; the 50-death reset stress test and 100-capture stability check remain the live integration checks.

## 2026-08-26 — Phase 1 environment completion

### Final validation

The completed environment loop now covers capture, observation conversion, action dispatch, death detection, reward, reset, and repeatable pacing. Final checks on `main`:

```text
unit tests:          9 passed
benchmark steps:     100
mean step time:      83.42 ms
decisions/sec:       11.99
reset stress deaths: 50
reset failures:      0
episode failures:    0
```

Phase 1 is complete. The next phase can establish a non-learning baseline, but PPO/DQN remains deferred until that baseline and evaluation protocol are defined.

## 2026-08-26 — Started the media archive

The 20-second 60 FPS episode recording at `artifacts/episodes/20260826T113120Z/episode.mp4` is worth preserving as a technical montage candidate. It shows the complete screen-state flow and reset story used to build Phase 1. Media selection and intended presentation use are now tracked in [`docs/media-log.md`](media-log.md); routine generated artifacts remain local and gitignored.

## 2026-08-26 — Started Phase 2 observation definition

### Baseline

Observation v1 remains a single `160×90` RGB frame. This gives us a simple, reproducible baseline before changing color representation or cropping the gameplay region.

### Next representation

The next implementation adds configurable frame stacking so a policy can observe recent motion rather than one isolated screenshot. The initial comparison will keep RGB and use four frames in oldest-to-newest order; grayscale and cropped-region variants come later. Object detection is intentionally deferred.

The media archive rule continues through Phase 2: preserve any episode that demonstrates a meaningful observation breakthrough, failure mode, or presentation-worthy result.

## 2026-08-26 — Added configurable RGB frame stacking

### Implementation

Added `frame_stack` to `GeometryDashEnv`. The default `frame_stack=1` preserves the single-frame RGB baseline. Setting `frame_stack=4` returns four observations in oldest-to-newest order with shape `(4, 90, 160, 3)`; reset fills the initial buffer with the first frame so the observation space is valid immediately.

### Validation

The environment test suite now passes 10 tests, including stack ordering. A live `frame_stack=4` reset and no-op step both returned `(4, 90, 160, 3)` observations accepted by the Gymnasium observation space. No grayscale conversion, cropping, object detection, or RL training was introduced.

## 2026-08-26 — Defined the Phase 3 cube action space

The initial action space remains `gymnasium.spaces.Discrete(2)`:

- `0` = do nothing
- `1` = jump

This is sufficient for cube gameplay. Hold/release actions are intentionally deferred until ship, wave, UFO, or robot modes are added. No action-space code was expanded in this step.

## 2026-08-26 — Defined the Phase 4 reward direction

### Baseline

The current terminal reward remains `-1 + progress_ratio`. It is useful for validating death detection and distinguishing early from late failures, but it is sparse and cannot teach fine-grained movement efficiently.

### Future shaping

The target design is based on `progress_delta`: a small survival reward, positive reward for newly achieved forward progress, a death penalty, and a larger completion reward. Absolute progress must not be rewarded repeatedly because the agent could receive credit for remaining at the same location.

No reward code was changed. First we need a reliable per-step progress measurement; otherwise shaping would add noise rather than learning signal.

## 2026-08-26 — Started Phase 5 non-learning baseline

Added `tools/baseline_agent.py` with three deliberately simple policies: always no-op, random jump, and jump every `N` decisions. It reports average terminal progress, best terminal progress, average episode length, death rate, progress sample count, and reset failures.

The same seed, episode count, maximum episode length, and environment settings must be used for future RL comparisons. No learning algorithm is included, and baseline episodes are not automatically recorded as video unless they produce a visually meaningful milestone.

## 2026-08-26 — Phase 5 baseline result

Command: `py -3.13 tools\\baseline_agent.py --episodes 10 --max-steps 300 --period 6 --seed 42`

```text
policy    episodes  avg_progress  best_progress  avg_length  death_rate  resets_failed
noop            10         0.010          0.019      10.400      100.0%             0
random          10         0.019          0.048      49.700      100.0%             0
periodic        10         0.009          0.011      10.400      100.0%             0
```

Random actions were strongest, reaching 4.8% best terminal progress and 1.9% average terminal progress. All policies died in every episode, and all reset attempts succeeded. Future RL comparisons must use this same protocol and beat these measurements. This routine baseline run produced no new montage-worthy video; the media archive remains active for future milestones.

## 2026-08-26 — Made learning proof and media evidence first-class deliverables

### Decision

The project now has three equal outcomes: build a credible RL agent, learn and explain the RL concepts used to build it, and preserve authentic footage for a future technical montage. A technical milestone alone is no longer the complete project story.

### Learning evidence

Added `docs/learning/README.md` with a just-in-time curriculum from MDP/POMDP framing through returns, Bellman reasoning, exploration, tabular Q-learning, pixel representations, DQN, PPO trade-offs, training discipline, and multi-seed evaluation. A module counts as learned only when it contains an own-word explanation, a pre-run prediction, an exercise or implementation, measured evidence, a reflection, a Geometry Dash connection, and an assistance disclosure.

The curriculum is a plan, not a retroactive claim of mastery. Its modules remain incomplete until the learner creates and reviews the required evidence.

### Media evidence

Added `docs/montage-plan.md` with a planned M00–M22 shot list and triggers for irreplaceable moments such as the first correct reward trace, first learning signal, first baseline-beating checkpoint, progress milestones, first completion, controlled failure/fix, and final held-out comparison. Upgraded `docs/media-log.md` into a catalog of footage that actually exists, including checksum, backup, privacy, rights, and evidence-link requirements.

The existing `20260826T113120Z` state-flow recording remains a candidate. Its SHA-256 is now recorded in the media log, but it is not considered safely preserved until a second backup and the privacy/rights reviews are recorded.

## 2026-08-26 — Started L0: Geometry Dash as an MDP/POMDP

Created `docs/learning/00-geometry-dash-as-an-mdp.md` as a guided worksheet. Verified code facts are prefilled, but all explanations, the temporal-observation prediction, the transition example, comprehension answers, and later reflection remain explicitly assigned to the learner.

L0 is not marked complete. The next verification pause is a review of the learner's own answers about the agent, environment, state versus observation, and one-frame versus frame-stack prediction.

## 2026-08-26 — Deferred L0 and started reproducible development setup

The learner chose to postpone the MDP/POMDP worksheet and start implementation work. L0 remains explicitly incomplete and is marked deferred rather than silently treated as learned.

### Packaging decision

Added `pyproject.toml`, `.python-version`, and `uv.lock`. ADR 0002 selects `uv`, pins the default interpreter to Python 3.13, declares support for Python `>=3.12,<3.14`, and keeps future training dependencies out of the environment until algorithm selection.

Removed `requirements.txt` so dependencies cannot drift across two sources of truth. The original broken Python 3.11 environment was not deleted; after stopping the verified VS Code Jedi process holding it open, it was moved to the ignored `.venv-broken-20260826` recovery directory. `uv sync --dev` then created a clean Python 3.13.14 `.venv`.

### Package boundary refactor

Moved screen-state detection and Windows control into `src/geometry_dash_env`. The library no longer imports runtime implementation from the top-level `tools` package, tests and scripts now import `geometry_dash_env`, and compatibility tool modules keep existing commands usable.

### Verification and regression

The first clean-environment test run exposed one stale mock path in the bbox test. Because the mock still targeted `src.geometry_dash_env`, the test called the real Win32 function with fake handle `123` and failed with `WinError 1400`. Updating the mock to the installed package path fixed the regression.

Final results:

```text
Python:                 3.13.14
Locked packages:        12
Dependency check:       compatible
Offline tests:          10 passed
Source distribution:    built
Wheel:                  built
Isolated wheel import:  passed
Capture tool --help:    passed
Baseline tool --help:   passed
```

## 2026-08-26 — Added pinned offline quality gates and Windows CI

Pinned Ruff 0.16.4, Pyright 1.1.411, Coverage.py 7.15.4, and pre-commit 4.6.2 in the development dependency group. Added `pyrightconfig.json`, `.pre-commit-config.yaml`, and branch-aware coverage configuration with a 60% floor for testable package logic; the Win32 input module is excluded because it requires a live desktop.

Added `.github/workflows/quality.yml`, a Windows matrix for the explicitly supported Python 3.12 and 3.13 interpreters. The workflow installs from `uv.lock`, runs formatting, linting, type checking, offline tests with coverage, and package build as separate steps, and asserts that no proprietary Geometry Dash directory is present.

The first pre-commit run fixed trailing whitespace in two pre-existing documentation files. After that cleanup, pre-commit passed. A new nullable-window guard briefly broke two reset tests whose mocks did not model `_ensure_window()`; the tests were corrected to provide a fake handle, and the full test suite passed again.

## 2026-08-26 — Preserved the pre-refactor prototype baseline

Created the annotated tag `prototype-baseline-8d4e496` at commit `8d4e496` (`baseline: add non-learning policy comparison`). The tag is the fixed comparison point for packaging, quality-gate, and future environment-hardening changes; it contains no later refactor or CI files.

## 2026-08-26 — Recorded the live experiment host fingerprint

Added `docs/experiment-environment.md` with the observed Windows edition/build, CPU, GPUs and driver versions, installed RAM, active display, 150% scaling, 2560×1600/240 Hz display mode, and current 800×600 Geometry Dash client capture. The document explicitly distinguishes current-host evidence from historical-run equivalence and leaves unrecoverable in-game settings open rather than guessing.

## 2026-08-26 — Recorded the locked test interpreter

Added CPython `3.13.14` to the experiment fingerprint. This is the interpreter used by `uv run` for the successful 10-test run and package checks; the supported project range remains `>=3.12,<3.14`.

## 2026-08-26 — Documented the unrecoverable Geometry Dash version

The local `GeometryDash.exe` has no usable Windows version-resource fields, and no standard Steam app manifest was present. The running process and executable path are confirmed, but an exact game release cannot be inferred responsibly. The roadmap item remains open until an in-game UI or store-version capture is recorded.

## 2026-08-26 — Recorded the live level while preserving settings uncertainty

A focused screenshot confirmed `Stereo Madness`, an `800×600` client capture, `Attempt 305`, and a `1%` results state. Window mode, VSync/FPS, character mode, and game speed were not visible or recoverable, so `docs/experiment-environment.md` records them as open evidence gaps rather than treating the Python controller's 60 FPS target as a game setting.

## 2026-08-26 — Recorded video encoder provenance

Recorded `ffmpeg 8.1.1-full_build-www.gyan.dev` and verified the candidate episode as a 20-second, 1,200-frame H.264 MP4 at 800×600 and 60 FPS. Encoding was enabled for the recorder run; benchmark commands remain non-video measurements.

## 2026-08-26 — Backed up the selected state-flow video

Copied `artifacts/episodes/20260826T113120Z/episode.mp4` to the ignored local path `media-backups/20260826T113120Z/episode.mp4` before cleanup. The source and backup are both 1,082,879 bytes and have matching SHA-256 hashes; metadata and selected PNG evidence still need separate preservation work.

## 2026-08-26 — Added a machine-readable media checksum manifest

Added `docs/media-checksums.sha256` with hashes for the source MP4, its `metadata.json` sidecar, and the ignored backup copy. The source and backup hashes match exactly; the metadata hash is recorded separately so later edits are detectable.

## 2026-08-26 — Documented the implemented command surface

Added `docs/command-surface.md` and linked it from the README. Capture, environment benchmark, non-learning baseline, recording, offline detector, episode scan, reset stress, and capture-stability commands are listed with their live/offline requirements. Training and evaluation commands remain absent because no algorithm, checkpoint format, reward protocol, or held-out evaluation protocol has been accepted yet.

## 2026-08-26 — Chose uv as the developer task runner

Added `docs/developer-commands.md` with canonical PowerShell commands for setup, formatting, linting, type checking, tests, coverage, pre-commit, packaging, offline analysis, and live smoke tools. `uv` is the task runner because it already owns the pinned interpreter, lockfile, synchronization, and project command execution. `train` and `evaluate` remain future commands until their protocols are real.

## 2026-08-26 — Added the PowerShell task runner

Added `scripts/dev.ps1` with named tasks for setup, format, lint, typecheck, test, test-offline, test-live, benchmark, train, and evaluate. Live tasks require an explicit `-ConfirmLive`; train/evaluate return exit code 2 with an actionable message until the learning protocol is implemented.

## 2026-08-26 — Exported a historical dependency snapshot

Added `docs/dependency-snapshot-20260826.txt` from `uv pip freeze --exclude-editable`. It is explicitly labeled as provenance only; the project continues to install from `pyproject.toml` and `uv.lock`.
