# Reward Contract v1

The first locked baseline is sparse terminal reward:

- alive gameplay and transition decisions: 0.0;
- detected death/results: -1.0 plus terminal progress ratio;
- detected completion: +1.0;
- time-limit truncation and invalid-state controller outcomes: 0.0.

Terminal progress is included once, only in the death/results outcome. The
current live environment detects results but not completion, so the
completion term is a tested contract primitive for the future completion
detector rather than a current live claim.

Every reward result exposes separate progress, survival, death, completion,
truncation, invalid_state, and total components. The baseline has no survival
shaping and no per-step progress reward. This means standing still, repeating
a frame, and reset/transition UI cannot accumulate meaningful progress
reward. Missing progress contributes zero progress component and leaves the
death penalty at -1.0.

The contract is versioned as reward-sparse-terminal-v1. Any shaped alternative
requires a separate protocol, ablation, and comparison against evaluation
progress/completion before it can replace this baseline.
