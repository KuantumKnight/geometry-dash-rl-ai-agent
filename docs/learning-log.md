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
