# Experiment Protocol v1

The primary research question for v1 is: **Can a pixel policy complete Stereo
Madness more reliably than the locked non-learning baselines under the same
interaction budget?** The primary metric is completion rate; median terminal
progress, best progress, episode length, deaths, truncations, reset failures,
wall time, and environment steps are secondary metrics.

Training and evaluation are separate. Training has a predeclared environment
step and wall-clock budget. Model selection uses validation episodes only. Final
held-out evaluation uses an independent episode set and seed list and is not
repeated to select checkpoints. A run beats the baseline only when its point
estimate is higher and its uncertainty interval does not overlap the baseline's
predeclared tie band; otherwise the result is tied or inconclusive.

`configs/baseline.json` is the committed reference configuration. It records
environment, observation, reward, algorithm, training, evaluation, recording,
and system sections. `resolve_config` rejects unknown sections/keys, resolves
defaults, and hashes the canonical result. `RunManager.create` writes the
resolved config and metadata before interaction begins, including UTC times,
git SHA and dirty-tree status, command, Python/platform, contract versions,
seed values, and config hash.

Run directories contain `metadata.json`, `resolved-config.json`, append-only
`telemetry.jsonl` and `episodes.jsonl`, atomic JSON checkpoints, `summary.json`,
and `report.md`. States are `created`, `running`, `interrupted`, `failed`,
`completed`, and `evaluated`. Interruption preserves prior records; resuming
requires the interrupted state and does not reset counters or overwrite raw
metrics. Checkpoints are verified immediately after atomic save.

The repository implementation is offline-testable with:

```powershell
uv run python -m unittest tests.test_experiment tests.test_baselines -v
```

Live baseline episodes, confidence intervals, checkpoint selection evidence,
and full launch/resume reproduction remain measurement gates. Geometry Dash
capture/input scheduling is not fully seed-controlled, so exact live replay is
not promised even when policy and library seeds match.
