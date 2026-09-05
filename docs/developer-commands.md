# Developer commands

`uv` is the Windows-friendly task runner for this repository. It discovers the pinned Python interpreter, installs from `uv.lock`, and executes commands inside the project environment. Run these from the repository root in PowerShell.

## Setup and quality

```powershell
uv sync --dev
uv run ruff format src tests tools
uv run ruff check src tests tools
uv run pyright
uv run coverage run -m unittest discover -s tests -v
uv run coverage report
uv run pre-commit run --all-files
uv run python -m build
```

## Tests and offline analysis

```powershell
uv run python -m unittest discover -s tests -v
uv run coverage run -m unittest discover -s tests -v
uv run coverage report
uv run python tools\scan_episode.py --help
uv run python tools\benchmark_detector_offline.py --help
uv run python tools\evaluate_detector.py --help
```

These commands do not launch Geometry Dash or send desktop input. The default test discovery contains only offline contract tests.

The detector evaluator consumes ground-truth annotation JSONL plus prediction
JSONL with matching `frame_id`, `episode_id`, `timestamp_utc`, and
`state` fields. It emits JSON with a confusion matrix, per-state
precision/recall/F1, and transition latency. Example:

uv run python tools\evaluate_detector.py --ground-truth path\to\ground-truth.jsonl --predictions path\to\predictions.jsonl --split held_out --output artifacts\detector-evaluation.json

Predictions must cover exactly the selected ground-truth frame IDs. This
prevents silent omission of difficult samples from the reported metrics.

## Live smoke/benchmark commands

Start a legitimate, visible Geometry Dash installation first and verify desktop focus is safe:

```powershell
uv run python tools\capture_action.py --help
uv run python tools\benchmark_env.py --help
uv run python tools\baseline_agent.py --help
uv run python tools\record_frames.py --help
uv run python tools\stress_reset.py --help
uv run python tools\verify_capture_stability.py --help
```

Use the actual operation flags only after reading each tool's help. Live commands fail early when the configured executable or visible window is unavailable.

## Future commands

`train` and `evaluate` are deliberately not listed as runnable commands yet. They become part of this surface only after the reward, algorithm, checkpoint, and held-out evaluation decisions are implemented and documented.

## Shell completion decision

Shell completion is intentionally deferred until the command names and flags stabilize. The current `scripts/dev.ps1` `ValidateSet` is the single source for task names; generating completion now would encode provisional `train`/`evaluate` behavior and create another surface to keep synchronized.
