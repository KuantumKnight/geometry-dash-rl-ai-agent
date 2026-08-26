# Emergency stop

Every live environment owns an `EmergencyStop` latch. The operator-facing host should bind `Ctrl+Shift+F12` to `env.emergency_stop.request()` (or to `stop.request()` when a shared latch is injected). The next step checks the latch before dispatching any action and halts the episode with an explicit error; no further input is sent until the latch is cleared.

```python
from geometry_dash_env import EmergencyStop, GeometryDashEnv

stop = EmergencyStop()
env = GeometryDashEnv(emergency_stop=stop)
# Host hotkey callback: stop.request()
# Before a new controlled run: stop.clear()
```

The environment does not register a global hotkey itself, avoiding hidden OS hooks. The host that owns the live session must make the `Ctrl+Shift+F12` binding visible to the operator.
