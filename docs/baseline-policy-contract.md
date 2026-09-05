# Baseline Policy Contract

Phase 4 baselines are importable from `geometry_dash_env.baselines` and all
return only the locked `Discrete(2)` actions: `0=noop` and `1=jump`.

`AlwaysNoopPolicy` is deterministic. `RandomJumpPolicy` owns a private
`random.Random(seed)` stream, so equal seeds reproduce equal action sequences
without changing process-global randomness. `PeriodicJumpPolicy` jumps on
one-based decision intervals and rejects non-positive periods.
`BrightnessHeuristicPolicy` is a deliberately simple observation-based policy:
it jumps when the mean brightness of the bottom observation band is below its
configured threshold. It has no learned state or training dependency.

Offline validation:

```powershell
uv run python -m unittest tests.test_baselines -v
```

The live baseline protocol still requires the same environment, observation,
and reward contract as learning agents, multiple independent seeds, enough
episodes for uncertainty intervals, episode-level artifact retention, and a
rerun whenever a contract version changes. Those measurements are not claimed
by these unit tests.
