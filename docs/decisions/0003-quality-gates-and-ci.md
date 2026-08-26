# ADR 0003: Pinned quality gates and offline Windows CI

- Status: accepted
- Date: 2026-08-26
- Decision owners: project maintainer

## Context

The repository needs repeatable checks before RL code and experiment claims are added. The live game is proprietary, Windows-only, and unavailable in ordinary CI, so checks must exercise the package and offline fixtures without requiring Geometry Dash.

## Decision

Use a small pinned development toolchain:

- Ruff `0.16.4` for formatting and linting;
- Pyright `1.1.411` in basic mode for `src/`, `tests/`, and `tools/`;
- Coverage.py `7.15.4` with branch measurement and a 60% floor for testable package logic;
- pre-commit `4.6.2` with pinned Ruff `v0.16.4` and pre-commit-hooks `v6.0.0` revisions.

The Windows GitHub Actions workflow runs on Python 3.12 and 3.13, the explicitly supported interpreters. It installs with `uv.lock`, keeps formatting, linting, typing, tests/coverage, and packaging as separate visible steps, and caches dependency downloads rather than the project environment. It contains an explicit assertion that the proprietary `Geometry Dash/` directory is absent.

The Win32 input module is excluded from the coverage floor because it requires a live desktop and game window. Its behavior remains covered by the environment contract's mocked tests and by later live qualification runs; this exclusion is not a claim that live control is fully tested in CI.

## Consequences

Every pull request gets a deterministic offline signal before training or live experiments are considered. The 60% floor is intentionally an initial ratchet for the current prototype; it should rise as detector, reset, reward, and training logic gain focused tests. CI cannot validate focus, timing, capture, input injection, or copyrighted game assets.

## Verification

Local verification on 2026-08-26:

- `uv run pre-commit run --all-files` passed;
- `uv run ruff format --check src tests tools` passed;
- `uv run ruff check src tests tools` passed;
- `uv run pyright` passed with 0 errors;
- 10 offline unit tests passed;
- coverage reported 62% against the 60% floor;
- `uv run python -m build` produced both sdist and wheel;
- the wheel imported successfully in an isolated environment;
- the workflow YAML parsed successfully with PyYAML.

The public GitHub Actions result remains pending until this branch is pushed.
