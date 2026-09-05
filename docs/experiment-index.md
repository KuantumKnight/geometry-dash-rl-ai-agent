# Experiment Index

This index is the entry point for measured runs. It intentionally distinguishes
historical prototype evidence from experiments that satisfy the future locked
protocol.

## Historical evidence

| ID | Description | Status | Evidence |
| --- | --- | --- | --- |
| prototype-baseline-8d4e496 | Pre-refactor live environment | Historical | Git tag and docs/learning-log.md |
| env-benchmark-20260826 | 100-step live timing benchmark | Historical | docs/experiment-environment.md |
| reset-reliability-20260826 | 50 consecutive death/reset cycles | Historical | docs/experiment-environment.md |
| baseline-10-episodes-20260826 | No-op, random, and periodic policies | Historical | docs/learning-log.md |

These runs were collected on one machine before the current experiment
protocol, reward contract, and held-out evaluation split were locked. They are
not valid evidence of a trained-agent comparison.

## Required record for new runs

Each new experiment receives a stable ID and must link to:

- the research question, prediction, parent run, and decision;
- the exact git SHA and clean/dirty state;
- resolved config, contract versions, seed, and environment fingerprint;
- raw episode data, generated summary, and any checkpoint;
- representative media, checksums, and privacy/rights status.

The formal protocol is frozen in `docs/experiment-protocol.md`; new live
measurements should still be labeled exploratory until the reference setup and
baseline evidence satisfy the remaining Phase 4 gates.
