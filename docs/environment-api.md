# Environment API — Initial Smoke-Test Interface

The first environment wrapper is in `src/geometry_dash_env/environment.py`.

```python
from geometry_dash_env import GeometryDashEnv

env = GeometryDashEnv()
observation, info = env.reset()
observation, reward, terminated, truncated, info = env.step(0)
env.close()
```

## Observation

The environment captures the game client as RGB pixels and resizes each frame to `160×90`. The returned NumPy array has shape `(90, 160, 3)` and dtype `uint8`.

## Actions

- `0`: no-op
- `1`: jump using the space bar

## Current reward and termination

- Alive/transition frame: reward `0.0`, `terminated=False`
- Results screen detected: reward `-1.0`, `terminated=True`
- `truncated` is always `False` in this smoke-test wrapper

This is intentionally not the final reward design. The next iteration should add a time limit, a reliable gameplay-state classifier, progress-based reward, and a proper Gymnasium-compatible wrapper once the interaction loop is stable.
