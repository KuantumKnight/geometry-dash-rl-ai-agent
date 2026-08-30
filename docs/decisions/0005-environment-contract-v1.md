# ADR 0005: Accept Environment Contract v1

- Status: Accepted
- Date: 2026-08-31
- Scope: Phase 1 environment API and lifecycle

## Decision

Accept the current `GeometryDashEnv` contract as version 1 for offline
integration and future live qualification:

- observations are RGB `uint8` arrays in HWC order;
- the default observation shape is `(90, 160, 3)`;
- optional frame stacking is explicit and returns
  `(stack, 90, 160, 3)` in oldest-to-newest order;
- actions are `0` for no-op and `1` for jump;
- a detected results screen returns `terminated=True`;
- the configured decision limit returns `truncated=True`;
- reset and step diagnostics include contract versions and state-transition
  metadata;
- active input is suppressed outside validated `GAMEPLAY`;
- reset input is only sent from validated resettable states;
- `close()` is idempotent and context-manager cleanup is supported.

The contract is protected by offline fake-backend tests and the public
Windows CI matrix. The current environment version is
`phase1-contract-v1`.

## Limitations accepted for v1

- Death and completion are currently represented through the results-screen
  detector; completion does not yet have a separate state or reward.
- The detector is heuristic and has not been qualified on a held-out,
  multi-episode dataset.
- Progress is only estimated from results screens; continuous progress and
  reward shaping remain deferred.
- Geometry Dash is a live, external process, so Gymnasium reset
  determinism cannot include game physics or OS scheduling.
- Window movement or resizing during an episode terminates the episode and
  requires a new reset.
- Live 1,000-step and 100-reset qualification has not yet been completed.

These limitations prevent training-readiness claims but do not block using
the contract as the stable boundary for the next detector and reward work.

## Consequences

Consumers can persist and compare observations, actions, termination flags,
and diagnostic metadata against a named contract version. Future changes to
these semantics require a new environment contract version and a follow-up
ADR rather than silently changing v1 behavior.
