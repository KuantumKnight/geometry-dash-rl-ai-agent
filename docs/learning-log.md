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
