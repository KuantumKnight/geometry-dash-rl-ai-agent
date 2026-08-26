# Code-quality review checklist

This review is run before a refactor removes or consolidates code. The goal is to distinguish dead code from compatibility, comparison, and evidence code that is intentionally retained.

## 2026-08-26 review

- [x] Ruff unused-import/name checks pass for `src/`, `tests/`, and `tools`.
- [x] Public package code has one implementation path under `src/geometry_dash_env`.
- [x] `tools/game_state.py` is an intentional compatibility re-export; it is not a second detector implementation.
- [x] `tools/benchmark_detector_offline.py` intentionally retains the old pixel-loop detector so the NumPy rewrite can be compared for equivalence and speed.
- [x] No generated artifacts, local game files, or `.venv` content are imported by package code.
- [x] The top-level tools are still used as public command surfaces and are not dead scripts.
- [x] Current reset messages say “clicking retry”; the earlier “pressing R” wording remains only in the chronological learning log as historical context.
- [ ] Run a dedicated dead-code scanner after the package API and training modules stabilize; early scanner output would misclassify compatibility and future entrypoints.

## Refactor rule

Do not delete a seemingly unused function until its import graph, CLI surface, compatibility role, benchmark role, and documentation references have been checked. Record removals in the learning log and preserve a focused regression test when behavior changes.
