# Decision 0001: Define the Environment Before the Agent

**Date:** 2026-08-26  
**Status:** Accepted

## Decision

The first implementation milestone will be a minimal game environment rather than an RL algorithm.

The environment should eventually expose a small interface:

- `reset()` starts or restores an episode and returns the initial observation.
- `step(action)` applies one action and returns the next observation, reward, termination state, and diagnostic information.

## Reasoning

An RL algorithm cannot be meaningfully evaluated until observations, actions, rewards, termination, and reset behavior are reliable. Proving this loop first reduces the risk of tuning an agent around a broken or inconsistent interface.

## Open questions

- Which screen-capture method provides stable frames on this Windows setup?
- Can jump and no-op actions be sent without affecting normal desktop use?
- What visual or process signal reliably indicates death?
- Should the first observation be a cropped image, a downsampled image, or extracted features?
