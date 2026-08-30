# Environment API — Gymnasium-Compatible Interface

The first environment wrapper is in `src/geometry_dash_env/environment.py`.

```python
from geometry_dash_env import GeometryDashEnv

env = GeometryDashEnv()
observation, info = env.reset()
observation, reward, terminated, truncated, info = env.step(0)
env.close()
```

`GeometryDashEnv` inherits from `gymnasium.Env`, exposes `action_space` as
`gymnasium.spaces.Discrete(2)`, and exposes `observation_space` as a
`gymnasium.spaces.Box` matching the configured observation shape and dtype
`uint8`.

## Observation

The environment captures the game client as RGB pixels and resizes each frame to `160×90`. The returned NumPy array has shape `(90, 160, 3)` and dtype `uint8`. The canonical layout is RGB `HWC`; channel-first consumers must transpose it in an explicit wrapper rather than changing the environment contract.

This is observation v1. The environment can optionally stack the most recent
frames with `frame_stack=4`, returning shape `(4, 90, 160, 3)` in
oldest-to-newest order. The default remains `frame_stack=1` so the single-frame
baseline stays reproducible while representations are compared.

## Actions

- `0`: no-op
- `1`: jump using the space bar

Phase 3 intentionally keeps cube gameplay to these two actions. Hold/release
semantics are deferred until other Geometry Dash modes—ship, wave, UFO, or
robot—are explicitly supported.

## Current reward and termination

- Alive/transition frame: reward `0.0`, `terminated=False`
- Results screen detected: reward `-1.0 + progress_ratio`, `terminated=True`
- Time limit reached: `truncated=True`, `terminated=False`

Terminal results include `info["termination_reason"] = "results_screen"`.
Time-limit truncation includes `info["truncation_reason"] = "max_steps"`.
The other reason field is `None` for each respective outcome.

The `progress_ratio` is estimated from the normal-mode green progress bar on the results screen and is included in `info`. For example, an attempt ending at 50% receives approximately `-0.5`. This is a terminal progress signal, not yet a continuous reward.

The next reward design must use per-step `progress_delta`, not absolute progress. Reusing absolute progress would allow repeated observations at the same location to receive reward without actual advancement. Survival, death, and completion shaping remain deferred until a reliable per-step progress signal exists.

## Timing

Capture remains paced at 60 FPS by default using monotonic frame deadlines. The environment repeats each chosen action for `frame_skip=4` frames, so the policy targets approximately 15 decisions per second while the pixel timing remains available. Set `frame_skip=1` for one decision per captured frame.

The default time limit is `max_steps=900` decisions. The historical measured rate of 11.99 decisions/sec implies approximately 75 seconds, not 60; the actual wall time varies with capture and scheduling load. Reaching the limit returns `truncated=True`.

This is intentionally not the final reward design. The next iteration should add continuous progress tracking and evaluate the environment with a non-learning baseline once the interaction loop is stable.

## Lifecycle and reset options

`close()` is idempotent, and the environment can be used as a context manager:

```python
with GeometryDashEnv() as env:
    observation, info = env.reset()
```

`reset(seed=...)` seeds Gymnasium's local RNG bookkeeping only; it cannot seed
Geometry Dash's physics or input/capture scheduling. The current live adapter
does not support reset options. Passing a non-empty `options` dictionary raises
`ValueError` so unsupported configuration is never silently ignored.

The initial client bounding box must remain fixed during an episode. A move or
resize raises a reset-required error and marks the episode inactive; see
[ADR 0004](decisions/0004-window-geometry-policy.md).

After a time-limit truncation, `step()` remains disabled until a reset has
been accepted from a resettable game state. The live controller does not
force-click an active gameplay screen merely because the Python time limit was
reached.
