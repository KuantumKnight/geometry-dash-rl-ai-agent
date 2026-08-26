# Project Roadmap

This roadmap is intentionally incremental. Each stage should produce a working artifact and a documented lesson.

## Stage 0 — Project foundation

- [x] Create the repository
- [x] Define the documentation workflow
- [x] Define the first environment interface
- [ ] Record the local game and tool versions

## Stage 1 — Game interaction prototype

- [x] Capture a game frame
- [x] Send a no-op and jump action
- [x] Detect a game-over state (baseline pixel heuristic)
- [x] Reset the game reliably (retry-button click validated)
- [x] Measure whether the interaction loop runs fast and stable enough

The jump action has been manually validated; the checklist remains open until it is covered by a repeatable test.

## Stage 2 — Gym-style environment

- [x] Implement `reset()` and `step(action)`
- [x] Define the observation representation
- [x] Define the action space
- [x] Define reward and termination rules
- [x] Add a small manual smoke test

## Phase 1 — Finish the environment

- [x] Replace fixed frame sleeps with deadline-based pacing
- [x] Reach approximately 12 decisions/sec with `frame_skip=4` at 60 FPS
- [x] Complete 50 consecutive deaths and resets with zero reset failures
- [x] Refresh capture bounds when the game window moves or resizes
- [x] Expose Gymnasium-compatible action and observation spaces
- [x] Add reset, jump, death, reward, timing, and capture contract tests

### Final validation

The final environment passed 9 unit tests, completed a 100-step benchmark at 83.42 ms mean step time / 11.99 decisions per second, and completed a 50-death stress run with zero reset failures. PPO/DQN and the non-learning baseline remain intentionally deferred to the next phase.

## Phase 2 — Define the RL problem properly

- [x] Establish observation v1 as a 160×90 RGB frame
- [x] Add configurable temporal frame stacking
- [ ] Compare RGB, grayscale, and cropped gameplay observations
- [ ] Choose a training representation based on speed and task performance
- [x] Defer object detection until a simple pixel baseline is evaluated
- [ ] Preserve montage-worthy videos and key frames for each meaningful experiment

## Stage 3 — Baseline agent

- [ ] Establish a simple non-learning baseline
- [ ] Choose an RL algorithm based on the environment and observations
- [ ] Run a short reproducible training experiment
- [ ] Record results and failure modes

## Phase 3 — Action space

- [x] Define cube action `0` as no-op
- [x] Define cube action `1` as jump
- [x] Keep the initial action space as `Discrete(2)`
- [ ] Add hold/release actions only when supporting ship, wave, UFO, or robot modes

## Phase 4 — Reward design

- [x] Use the provisional terminal reward `-1 + progress_ratio`
- [ ] Obtain a reliable per-step progress measurement
- [ ] Replace absolute progress reward with `progress_delta`
- [ ] Add a small survival reward only after timing and progress are validated
- [ ] Add distinct death and level-completion rewards
- [ ] Compare sparse terminal and shaped reward behavior with the same baseline

## Phase 5 — Non-learning baseline

- [x] Measure an always-no-op policy
- [x] Measure a random-jump policy
- [x] Measure a periodic-jump policy
- [x] Record average progress, best progress, episode length, death rate, and reset failures
- [x] Require future RL agents to beat the baseline on the same protocol

## Stage 4 — Iteration and evaluation

- [ ] Improve observations, rewards, or model architecture based on evidence
- [ ] Compare experiments using consistent metrics
- [ ] Save checkpoints and evaluation videos or summaries
- [ ] Document conclusions and limitations
