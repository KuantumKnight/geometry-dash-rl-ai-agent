# L0 — Geometry Dash as an MDP/POMDP

**Status:** In progress — learner answers required

**Started:** 2026-08-26

**Related implementation:** `src/geometry_dash_env/environment.py`

**Related contract:** `docs/environment-api.md`

## Purpose

Before choosing DQN, PPO, or another algorithm, define exactly what the agent interacts with. This worksheet separates the real game state from the pixels currently available to the policy and records a prediction about temporal observations before training begins.

The prompts marked **Learner answer** must be completed in the learner's own words. They are intentionally not prewritten by an assistant.

## Part A — What I think before studying

### A1. What is the agent in this project?

**Learner answer:**

> TODO

### A2. What is the environment?

Include what belongs to Geometry Dash and what belongs to the Python wrapper.

**Learner answer:**

> TODO

### A3. What is the difference between state and observation here?

Name information that exists in the game but may not be recoverable from one screenshot.

**Learner answer:**

> TODO

### A4. Is this fully observable or partially observable? Why?

**Learner answer:**

> TODO

## Part B — Verified project facts

These facts come from the current code and tests. They are scaffolding, not proof that the RL concepts are understood.

| Question | Current project fact |
| --- | --- |
| What reaches the policy? | A resized RGB game-client frame, currently `160×90×3`, with optional temporal stacking. |
| What actions exist? | `0 = no-op`, `1 = jump` using a short space-bar press. |
| What starts an episode? | `reset()` waits for a coarse gameplay/transition classification and initializes the observation buffer. |
| What currently ends an episode? | A detected results screen sets `terminated=True`; reaching `max_steps` sets `truncated=True`. |
| What reward exists now? | Zero during the attempt; terminal reward is approximately `-1 + progress_ratio`. |
| What is not implemented? | A trained policy, validated per-step progress reward, completion detection, and a robust multi-state classifier. |
| What timing exists? | Screen capture targets 60 FPS and one policy decision repeats across `frame_skip=4` captured frames by default. |

## Part C — Map the RL interaction loop

Fill the **Meaning in my words** column without copying the verified-fact wording.

| RL term | Project implementation/evidence | Meaning in my words |
| --- | --- | --- |
| Agent | Future policy/model choosing action `0` or `1` | TODO |
| Environment | Geometry Dash plus the Python capture/control/reset wrapper | TODO |
| Observation `o_t` | Current frame or ordered frame stack | TODO |
| Hidden/true state `s_t` | Game variables such as position, velocity, mode, collision state, and level time | TODO |
| Action `a_t` | No-op or jump | TODO |
| Reward `r_t` | Current terminal progress-based signal; future version not yet accepted | TODO |
| Policy `π(a|o)` | Not implemented yet | TODO |
| Episode | One attempt from valid gameplay until death, completion, or truncation | TODO |
| Terminal | Currently detected results/death; completion still missing | TODO |
| Truncation | Time limit or future external/environment interruption | TODO |

## Part D — Walk through one transition

Describe one concrete interaction using this structure:

```text
observation o_t
    → policy chooses action a_t
    → environment applies the action
    → game advances
    → reward r_t and next observation o_(t+1) are returned
```

**Learner example:**

> TODO: describe what the pixels show, which action is selected, what changes, and what reward/termination is returned.

## Part E — Why one frame may not be Markov

For the Markov property, the current state representation must contain enough information to predict the relevant distribution of the next state and reward after an action.

List at least three pairs of situations that could look similar in one frame but require different understanding because of hidden motion/history.

1. TODO
2. TODO
3. TODO

Candidate hidden variables to evaluate—not copy as the final answer—include vertical velocity, whether a jump was just pressed, animation phase, scroll velocity, game mode, and recent frames.

## Part F — Pre-experiment prediction

This prediction must be committed before the observation comparison or RL training result is known.

### Question

For early cube gameplay, which input do you predict will support better learning under the same training budget?

- one RGB frame;
- four stacked RGB frames; or
- another representation you can justify.

### Prediction

**Chosen representation:** TODO

**Why I expect it to help:**

> TODO

**Cost or downside I expect:**

> TODO

**What result would prove my prediction wrong:**

> TODO

## Part G — Diagram

Create and commit a simple diagram showing:

```text
game pixels → observation transform → policy → action
     ↑                                  ↓
state/reset detector ← reward/terminal ← game advances
```

- [ ] Diagram exists and is linked here.
- [ ] It distinguishes the unobserved game state from the pixel observation.
- [ ] It shows both the policy loop and the controller/reset responsibility.

**Diagram link:** TODO

## Part H — Comprehension check

Answer without referring to the definitions above.

1. Why are pixels called an observation rather than the full game state?
2. Why can frame stacking help even when the newest frame already shows the player and obstacle?
3. What is the difference between `terminated` and `truncated` in this environment?
4. Why should menu/results frames normally be controlled by the environment rather than learned as ordinary policy observations?

**Learner answers:**

1. TODO
2. TODO
3. TODO
4. TODO

## Part I — Reflection after implementation/experiment

Complete this only after the first controlled observation comparison.

### What matched my prediction?

> TODO

### What surprised me?

> TODO

### What changed in my mental model?

> TODO

### What remains uncertain?

> TODO

## Evidence and verification

- [ ] All learner-answer sections are complete in the learner's own words.
- [ ] The transition example is internally consistent with the environment API.
- [ ] At least three hidden-state/ambiguity examples are present.
- [ ] The observation prediction was committed before the comparison result.
- [ ] The diagram distinguishes state, observation, policy, controller, and environment.
- [ ] The comprehension answers are technically correct after review.
- [ ] Links to the relevant code, tests, commit, and later experiment report are present.
- [ ] L0 status in `docs/learning/README.md` and `docs/roadmap.md` is updated only after review passes.

## Assistance disclosure

Codex created the worksheet structure and prefilled verified repository facts on 2026-08-26. It did not write the learner-answer, prediction, comprehension, or reflection sections. Future explanations, corrections, external resources, and AI assistance must be listed here.
