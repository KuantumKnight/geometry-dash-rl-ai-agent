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
