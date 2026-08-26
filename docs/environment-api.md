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

The environment captures the game client as RGB pixels and resizes each frame to `160×90`. The returned NumPy array has shape `(90, 160, 3)` and dtype `uint8`.

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

The `progress_ratio` is estimated from the normal-mode green progress bar on the results screen and is included in `info`. For example, an attempt ending at 50% receives approximately `-0.5`. This is a terminal progress signal, not yet a continuous reward.

## Timing

Capture remains paced at 60 FPS by default using monotonic frame deadlines. The environment repeats each chosen action for `frame_skip=4` frames, so the policy targets approximately 15 decisions per second while the pixel timing remains available. Set `frame_skip=1` for one decision per captured frame.

The default time limit is `max_steps=900` decisions, or approximately 60 seconds at the default settings. Reaching the limit returns `truncated=True`.

This is intentionally not the final reward design. The next iteration should add continuous progress tracking and evaluate the environment with a non-learning baseline once the interaction loop is stable.
