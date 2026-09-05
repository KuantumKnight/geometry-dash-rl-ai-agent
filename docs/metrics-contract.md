# Metrics Contract v1

`geometry_dash_env.metrics` provides deterministic offline aggregation for
append-only episode rows. The primary metric is completion rate. Secondary
metrics include median/best progress, mean episode length, deaths,
truncations, reset failures, and environment steps. Missing progress is omitted
from progress summaries rather than converted to zero.

`bootstrap_interval` returns a seeded percentile interval for the mean. The
seed, sample count, and confidence are explicit inputs, making report
regeneration deterministic. `RollingMetrics` retains raw return/progress lists
while producing a compact snapshot; it never replaces raw episode telemetry.

Rows should include `return`, `length`, `progress`, and `outcome`; optional
`reset_failures` and other timing/checkpoint fields remain preserved by the
run manager's append-only JSONL artifact. Step telemetry also preserves
detector confidence/errors and missed-deadline timing when supplied by the
environment loop. Real baseline confidence intervals
require the predeclared multi-seed live episode collection and are not implied
by the synthetic unit tests.

Validate with:

```powershell
uv run python -m unittest tests.test_metrics -v
```
