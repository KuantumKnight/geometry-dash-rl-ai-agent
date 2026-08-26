# Project Roadmap

This roadmap is intentionally incremental. Each stage should produce a working artifact and a documented lesson.

## Stage 0 — Project foundation

- [x] Create the repository
- [x] Define the documentation workflow
- [x] Define the first environment interface
- [ ] Record the local game and tool versions

## Stage 1 — Game interaction prototype

- [ ] Capture a game frame
- [ ] Send a no-op and jump action
- [x] Detect a game-over state (baseline pixel heuristic)
- [x] Reset the game reliably (retry-button click validated)
- [ ] Measure whether the interaction loop is fast and stable enough

The jump action has been manually validated; the checklist remains open until it is covered by a repeatable test.

## Stage 2 — Gym-style environment

- [ ] Implement `reset()` and `step(action)`
- [ ] Define the observation representation
- [ ] Define the action space
- [ ] Define reward and termination rules
- [ ] Add a small manual smoke test

## Stage 3 — Baseline agent

- [ ] Establish a simple non-learning baseline
- [ ] Choose an RL algorithm based on the environment and observations
- [ ] Run a short reproducible training experiment
- [ ] Record results and failure modes

## Stage 4 — Iteration and evaluation

- [ ] Improve observations, rewards, or model architecture based on evidence
- [ ] Compare experiments using consistent metrics
- [ ] Save checkpoints and evaluation videos or summaries
- [ ] Document conclusions and limitations
