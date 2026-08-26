# Reinforcement Learning Journey

This directory proves what was learned while building the Geometry Dash agent. It is not a collection of copied definitions. Each completed module must connect an RL idea to code, a prediction, measured evidence, and a reflection.

## Current learning status

The repository already demonstrates practical environment engineering: screen capture, actions, episode boundaries, reset control, Gymnasium contracts, timing measurements, frame stacking, terminal progress estimation, and non-learning baselines. The chronological evidence is in [`../learning-log.md`](../learning-log.md).

The repository does **not** yet claim mastery of RL algorithms or successful learning. The modules below remain unchecked until the learner completes and reviews their evidence.

## Active module

L0 is now in progress: [`00-geometry-dash-as-an-mdp.md`](00-geometry-dash-as-an-mdp.md). The worksheet exists, but it is not learning proof until the learner-answer, prediction, comprehension, and reflection gates are completed and reviewed.

## Evidence standard

A module is complete only when it contains all of the following:

- **Explain:** a short explanation written in the learner's own words.
- **Predict:** a falsifiable prediction written before running the exercise or experiment.
- **Build:** a calculation, minimal implementation, test, or project change.
- **Measure:** raw results and the command/config that produced them.
- **Reflect:** what matched the prediction, what did not, and what changed in the learner's mental model.
- **Connect:** an explicit link from the concept to the Geometry Dash environment.
- **Disclose:** a brief note describing any AI, tutorial, paper, or library assistance.

Code alone proves that something runs. This combination proves that the learner understands why it runs and how to evaluate it.

## Learning workflow for every module

1. Read or watch one primary learning resource.
2. Close the resource and explain the concept from memory.
3. Write a prediction before executing code.
4. Solve a tiny example by hand or from scratch.
5. Test the idea in a toy environment.
6. Apply the idea to Geometry Dash only after the toy result makes sense.
7. Commit the note, exercise, tests, and result together or in a clearly linked sequence.
8. Record a 20–60 second voiceover candidate when the concept produces a strong visual story.

## Module checklist

### L0 — Frame Geometry Dash as an RL problem

**Learn:** agent, environment, observation, state, action, reward, policy, episode, terminal state, and partial observability.

- [ ] Write `00-geometry-dash-as-an-mdp.md` in your own words.
- [ ] Identify the true game state versus the pixels available to the policy.
- [ ] Explain why a single frame may violate the Markov property.
- [ ] Map `reset()` and `step()` outputs to the RL interaction loop.
- [ ] List at least three hidden variables: velocity, recent input, animation phase, or equivalent.
- [ ] Predict whether one frame or a short frame history should perform better and why.
- [ ] Draw the observation → policy → action → game → reward/next-observation loop.
- [ ] Link each claim to the current environment code or an open roadmap task.

**Pass condition:** You can explain the project's MDP/POMDP choices without reading the code, and the note distinguishes state from observation correctly.

### L1 — Returns, discounting, and reward design

**Learn:** immediate reward, return, discount factor, sparse reward, shaped reward, reward hacking, and terminal reward.

- [ ] Calculate discounted returns by hand for at least two short trajectories.
- [ ] Explain how changing `gamma` changes preference for early versus late progress.
- [ ] Write the current terminal reward equation and evaluate it at 0%, 25%, 50%, 75%, and 100% progress.
- [ ] Identify at least five ways a poorly designed reward could be exploited.
- [ ] Predict how sparse terminal reward and `progress_delta` shaping will differ.
- [ ] Add reward-invariant tests before changing the production reward.
- [ ] Run a trace that logs each reward component and compare it with the prediction.
- [ ] Write a reward-design reflection and link the accepted ADR.

**Pass condition:** Hand calculations, implementation, and logged reward traces agree, and repeated identical progress cannot earn repeated progress reward.

### L2 — Policies, value functions, and Bellman reasoning

**Learn:** policy, state value, action value, Bellman expectation equation, Bellman optimality equation, bootstrapping, and temporal-difference error.

- [ ] Explain `V(s)` and `Q(s,a)` using one Geometry Dash obstacle situation.
- [ ] Calculate a Bellman backup by hand for a tiny two-action example.
- [ ] Explain why bootstrapping can learn before an episode completes.
- [ ] Implement a tiny deterministic environment with known optimal values.
- [ ] Implement value iteration or tabular evaluation without an RL library.
- [ ] Compare calculated values with the implementation output.
- [ ] Add tests for the known optimal policy/value.
- [ ] Write what the value estimate would mean for a screenshot near a spike.

**Pass condition:** The hand solution and program agree, and you can explain the target, current estimate, and TD error.

### L3 — Exploration and non-learning baselines

**Learn:** exploration versus exploitation, random policy, epsilon-greedy policy, bandits, baseline selection, and why “best run” is weak evidence.

- [ ] Implement an epsilon-greedy multi-armed bandit exercise from scratch.
- [ ] Predict the behavior of at least three epsilon values before running it.
- [ ] Plot average reward/regret across multiple seeds.
- [ ] Explain why each Geometry Dash baseline exists and what it controls for.
- [ ] Unit-test no-op, random, and periodic action sequences.
- [ ] Strengthen the baseline protocol with multiple seeds and uncertainty.
- [ ] Predict which baseline will perform best before rerunning it.
- [ ] Compare the prediction with episode-level results and explain the difference.

**Pass condition:** The baseline comparison is reproducible and includes uncertainty; the note explains why a learning agent must beat a locked baseline.

### L4 — Tabular Q-learning in a toy environment

**Learn:** Q-learning update, off-policy learning, learning rate, discount, epsilon schedule, convergence assumptions, and state discretization.

- [ ] Write the Q-learning update from memory and label every term.
- [ ] Perform several Q-updates by hand.
- [ ] Implement tabular Q-learning without a training library on a small discrete task.
- [ ] Add deterministic tests for one-step updates.
- [ ] Predict the effect of learning rate, gamma, and epsilon changes.
- [ ] Run multiple seeds and plot learning curves.
- [ ] Explain why raw Geometry Dash images cannot use a practical Q-table.
- [ ] Explain how function approximation replaces the table.

**Pass condition:** The toy agent reliably learns, tests verify its update equation, and the note explains why deep RL is needed for pixels.

### L5 — Pixels, CNNs, and temporal information

**Learn:** tensors, channel order, normalization, convolution, receptive fields, feature learning, frame stacking, and partial observability.

- [ ] Inspect and visualize the exact observation tensor seen by the model.
- [ ] Calculate observation and replay-buffer memory requirements.
- [ ] Explain convolution using a feature such as an edge, player, or spike.
- [ ] Compare RGB, grayscale, crop, resolution, and stack candidates under a locked protocol.
- [ ] Predict which representation will be fastest and which may learn best.
- [ ] Test tensor shape, dtype, range, channel order, and stack order.
- [ ] Explain what motion information a frame stack can reveal.
- [ ] Write a reflection separating evidence from visual preference.

**Pass condition:** The selected observation has measured latency/memory/task evidence, and the model receives the intended tensor layout.

### L6 — Deep Q-learning

**Learn:** neural Q-function, replay buffer, target network, Bellman target, epsilon schedule, target updates, and instability risks.

- [ ] Derive the one-step DQN target and loss for one sample.
- [ ] Calculate one target and TD error by hand.
- [ ] Explain why replay and a target network help stability.
- [ ] Implement or instrument a minimal DQN on a toy image/discrete-action task.
- [ ] Test replay sampling, terminal targets, target-network updates, and checkpoint round trips.
- [ ] Predict the effect of replay warm-up and target-update frequency.
- [ ] Plot loss, Q-values, epsilon, returns, and evaluation performance.
- [ ] List failure signals such as exploding Q-values, constant actions, or reward improvement without progress.

**Pass condition:** The toy task is learned across multiple seeds, checkpoint resume works, and the learner can explain every term in the update.

### L7 — Policy gradients and PPO comparison

**Learn:** stochastic policy, log-probability objective, advantage, actor/critic, on-policy data, clipping, entropy, and GAE at a conceptual level.

- [ ] Explain how a policy-gradient agent differs from DQN.
- [ ] Calculate a small policy-gradient direction or advantage example by hand.
- [ ] Explain PPO clipping and what problem it is intended to reduce.
- [ ] Identify which data PPO may reuse and which data it must discard.
- [ ] Compare DQN and PPO against this project's constraints: pixels, two actions, one slow live environment, and sample budget.
- [ ] Run both only on a tiny controlled task if needed to validate the comparison.
- [ ] Predict which is more suitable before measuring the smoke tests.
- [ ] Record the algorithm choice and rejected alternative in an ADR.

**Pass condition:** The algorithm choice follows project constraints and evidence, not popularity, and the learner can explain the trade-off.

### L8 — Training discipline and debugging

**Learn:** overfitting, underfitting, optimization versus environment bugs, checkpointing, gradient/parameter diagnostics, ablations, and one-variable experiments.

- [ ] Create a failure-classification checklist: environment, detector, reward, wrapper, algorithm, infrastructure, or evaluation.
- [ ] Add finite-value checks for observations, rewards, losses, gradients, and parameters.
- [ ] Predict expected behavior on a tiny sanity task before every new training stack.
- [ ] Verify that one update changes parameters.
- [ ] Verify deterministic checkpoint save/load on fixed observations.
- [ ] Run a resume test and compare pre/post-resume state.
- [ ] Diagnose one real failure using evidence before tuning hyperparameters.
- [ ] Write an experiment where only one principal factor changes.

**Pass condition:** A failed run produces a diagnosis and regression check, not a random bundle of parameter changes.

### L9 — Evaluation, uncertainty, and scientific claims

**Learn:** training versus evaluation, model selection, held-out tests, seeds, distributions, confidence intervals, paired comparisons, and reproducibility.

- [ ] Explain why the best seed is not the expected performance.
- [ ] Compute mean, median, standard deviation, and a confidence/bootstrap interval on example episode results.
- [ ] Define the primary metric and baseline-beating criterion before the main run.
- [ ] Separate training, validation/model selection, and final evaluation.
- [ ] Run multiple independent seeds and retain weak valid runs.
- [ ] Generate tables and plots from raw episode data.
- [ ] Check whether higher training reward corresponds to higher evaluation progress/completion.
- [ ] Write claims using exact scope: platform, level, mode, protocol, and sample size.

**Pass condition:** The final result includes variability, all valid planned seeds, baseline comparison, failure accounting, and a claim no broader than the evidence.

### L10 — Teach the system back

**Learn:** communication is the final comprehension test.

- [ ] Write a one-page explanation of the full loop without copying library documentation.
- [ ] Record a 2–5 minute walkthrough explaining observation, action, reward, algorithm, and evaluation.
- [ ] Explain one failed idea and how evidence changed the design.
- [ ] Explain the strongest result and its most important limitation.
- [ ] Answer likely reviewer questions in `docs/faq.md`.
- [ ] Link every quantitative claim to a run/report.
- [ ] Ask a technical reviewer to identify any unclear or unsupported explanation.
- [ ] Correct the documentation based on that review.

**Pass condition:** A reader can understand and reproduce the project, and the learner can answer “why?” at every major design choice.

## Suggested repository structure

```text
docs/learning/
├── README.md
├── 00-geometry-dash-as-an-mdp.md
├── 01-returns-and-rewards.md
├── 02-values-and-bellman.md
├── 03-exploration-and-baselines.md
├── 04-tabular-q-learning.md
├── 05-pixels-cnns-and-memory.md
├── 06-dqn.md
├── 07-ppo-comparison.md
├── 08-training-debugging.md
├── 09-evaluation-and-claims.md
├── 10-system-teach-back.md
└── exercises/
    ├── returns/
    ├── bandit/
    ├── tabular-q/
    └── deep-rl-sanity/
```

Create files when the module begins. Empty files and generated definitions are not evidence of learning.

## Learning entry template

Use this inside each module note.

```md
# [Concept]

## What I thought before
[Write from memory before studying or coding.]

## My explanation
[Explain in your own words.]

## Geometry Dash connection
[Point to the exact environment/agent behavior this concept affects.]

## Prediction made before the run
[A falsifiable expected outcome.]

## Exercise or implementation
- Code/tests:
- Command:
- Config:
- Commit:

## Result
[Raw result link plus a concise summary.]

## What surprised me
[Where prediction and evidence differed.]

## What I can now explain
[Specific claims, not “I understand RL.”]

## Open questions
[What remains unclear or untested.]

## Assistance disclosure
[Resources, people, libraries, and AI assistance; say what was verified personally.]
```

## GitHub proof checklist

- [ ] The learning index accurately distinguishes completed and incomplete modules.
- [ ] Notes use the learner's own explanations and project-specific examples.
- [ ] Predictions have timestamps or commits before the corresponding result.
- [ ] Exercises have tests and can run from the documented environment.
- [ ] Results link to raw data/config/commit rather than screenshots alone.
- [ ] Reflections include failures and changed beliefs.
- [ ] AI assistance is disclosed without presenting generated text as personal understanding.
- [ ] README claims link to the relevant learning module, implementation, and experiment.
- [ ] Important modules have short teach-back recordings available for the final project story.
