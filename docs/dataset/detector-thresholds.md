# Detector Qualification Thresholds

These thresholds are predeclared for the first held-out detector
qualification. They apply to the `held_out` split produced by the
screen-state annotation protocol and must be reported before any threshold
tuning is changed.

## Required metrics

- `results` and `level_complete` terminal-state recall: at least `0.98` each
  when the state has at least 20 held-out transition examples.
- False-terminal rate on non-terminal states: at most `0.01`.
- Overall held-out state accuracy: at least `0.95`.
- Every canonical state must have a confusion-matrix row, even when its
  support is zero; zero-support states are reported as insufficient evidence,
  not as passing.

The terminal recall threshold is prioritized over overall accuracy because a
missed terminal frame can contaminate episode boundaries and reset behavior.
The false-terminal threshold limits accidental early episode termination.

## Qualification procedure

Run:

`uv run python tools/evaluate_detector.py --ground-truth ground-truth.jsonl --predictions predictions.jsonl --split held_out --output detector-evaluation.json`

The JSON report must retain the selected split, sample and episode counts,
confusion matrix, per-state metrics, and transition-latency summary. A report
cannot be called qualified until its episode count, state support, and
threshold comparison are reviewed.
