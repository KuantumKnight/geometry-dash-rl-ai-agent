# ADR 0004: Reject Client Geometry Changes During an Episode

**Status:** accepted

**Date:** 2026-08-30

## Context

The observation transform assumes that every captured frame in an episode
covers the same Geometry Dash client area. Moving or resizing the game changes
the pixel-to-game mapping and can make a policy appear to see an unexplained
state change. Silently continuing would mix incompatible observations in one
episode.

## Decision

Mid-episode window movement and resizing are unsupported for environment v1.
`GeometryDashEnv._capture()` compares the current client bounding box with the
episode's initial box. A change ends the active episode, records the new box,
and raises an actionable reset-required error. The next reset revalidates the
window and establishes a new capture geometry.

## Consequences

- Operators must keep the game client position and size fixed during an episode.
- The environment fails closed instead of returning mixed-geometry pixels.
- A later contract may support geometry changes, but it must define an explicit
  observation transform and add live validation before changing this policy.

## Evidence

- `tests/test_environment.py::EnvironmentTests::test_capture_refreshes_moved_bbox`
  verifies the termination behavior with an injected platform backend.
- `src/geometry_dash_env/environment.py` implements the comparison and error.
