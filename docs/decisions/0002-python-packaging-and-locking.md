# Decision 0002: Use uv, Python 3.13, and an Installable src Package

**Date:** 2026-08-26

**Status:** Accepted

## Context

The original repository had four lower-bound dependencies in `requirements.txt`, no package metadata or lock file, and a broken local `.venv` on Python 3.11. Tests passed only through a global Python 3.13 environment containing unrelated dependency conflicts. The library also imported production code from the top-level `tools` package, while tests and scripts imported `src.geometry_dash_env` directly.

This prevented clean installation, isolated verification, and a trustworthy future training environment.

## Decision

- Use `uv` for Python discovery, locking, environment synchronization, and command execution.
- Pin the default project interpreter to Python 3.13 through `.python-version`.
- Declare support as `>=3.12,<3.14` in `pyproject.toml`.
- Store runtime and development dependencies in `pyproject.toml` and resolve them in `uv.lock`.
- Package only `src/geometry_dash_env` as the installable `geometry-dash-rl` distribution.
- Import the package as `geometry_dash_env`; do not use `src.geometry_dash_env`.
- Move screen-state detection and Windows control into the installable package. Keep top-level tools as command-line prototypes and compatibility entry points.
- Do not add PyTorch, Stable-Baselines3, or another training stack until the algorithm-selection milestone.

## Reasoning

Python 3.13 already passed the current environment tests. Current official PyTorch documentation supports Python 3.10–3.14 on Windows, and Stable-Baselines3 added official Python 3.13 support in release 2.8.0. Restricting the upper bound below Python 3.14 keeps the initial lock on the versions explicitly checked for both the current project and planned SB3 path.

`uv` is already installed on the development machine and provides a project-level Python pin, lock file, isolated environment, and reproducible `uv run` commands. A standard `src` package prevents repository-root import behavior from hiding packaging errors.

## Verification

The accepted environment passed:

```text
uv lock --check
uv sync --dev
uv pip check
uv run python -m unittest discover -s tests -v
uv run python -m build
uv run --isolated --no-project --with <wheel> python -c "import geometry_dash_env"
```

Recorded result:

- Python: 3.13.14
- Offline tests: 10 passed
- Dependency check: all 12 installed packages compatible
- Build artifacts: source distribution and wheel created
- Isolated wheel import: passed
- Tool help smoke tests: passed

## Consequences

- Contributors should use `uv sync --dev` and `uv run ...` rather than global Python commands.
- `requirements.txt` is removed to avoid a second, drifting dependency source.
- The old broken environment is temporarily preserved locally as `.venv-broken-20260826` and ignored by git; it can be deleted after the new environment is trusted and no recovery is needed.
- Windows control still initializes at package import time and the default game path still depends on the working directory. Those limitations remain Phase 1 work.
- Training dependencies will require a separate, explicit decision about CPU/CUDA installation and algorithm library.

## References

- [uv project Python versions](https://docs.astral.sh/uv/concepts/python-versions/)
- [uv project structure](https://docs.astral.sh/uv/concepts/projects/layout/)
- [PyTorch local installation support](https://pytorch.org/get-started/locally/)
- [Stable-Baselines3 documentation](https://stable-baselines3.readthedocs.io/)
