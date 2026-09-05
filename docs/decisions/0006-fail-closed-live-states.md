# ADR 0006: Fail Closed on Unrecoverable Live States

- Status: Accepted
- Date: 2026-09-05
- Scope: Phase 1 state and capture safety

## Decision

Pause, menu, focus-loss, invalid-window, and invalid-client-geometry
conditions are controller errors for the current environment contract.
The environment does not synthesize a gameplay observation, silently retry
input, or click through an unexpected screen.

When a capture or window-validation operation raises a runtime error, the
active episode is deactivated and the exception is propagated to the caller.
The caller must inspect the diagnostic/error record and perform an explicit
reset after the game is back in a validated resettable state.

During reset, a detected main menu or unknown screen also fails immediately.
The bounded recovery loop for delayed results, missed clicks, level-info
screens, and lost focus remains a separate follow-up task.

## Consequences

This policy prevents actions from being dispatched against a screen that has
not been classified as gameplay. It also means an orchestration layer must
distinguish controller failures from policy failures and must not blindly
resume an episode after an exception.
