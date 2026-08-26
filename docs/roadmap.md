# Geometry Dash RL — Master Build Checklist

This is the source of truth for turning the current prototype into a reproducible reinforcement-learning project, a verifiable RL learning journey, and a world-class public GitHub story.

Last audited: **2026-08-26**

Target platform: **Windows**

Current target: **Stereo Madness, cube mode, two actions (`noop` and `jump`)**

## Three equal project outcomes

1. **Engineering:** build and evaluate a trustworthy Geometry Dash RL agent.
2. **Learning:** understand RL by predicting, implementing, measuring, and explaining each major idea.
3. **Story:** preserve authentic, traceable video of the failures, breakthroughs, and final result for a future montage.

The implementation is not the only deliverable. A milestone is fully documented when it has technical evidence, learning evidence, and a deliberate media decision.

## How to use this checklist

- Work from top to bottom unless a task is explicitly marked parallel or stretch.
- Do not mark an item complete because code merely exists. Mark it complete only when its acceptance check passes and evidence is recorded.
- Put experiment results in a dedicated experiment report; keep `learning-log.md` as the chronological engineering journal.
- Make one focused commit per coherent milestone. Include the verification command and result in the commit or pull-request description.
- Do not tune the agent to compensate for an environment bug. Fix and revalidate the environment first.
- Use [`learning/README.md`](learning/README.md) for concept modules, predictions, exercises, and reflections written in the learner's own words.
- Use [`montage-plan.md`](montage-plan.md) for planned shots and [`media-log.md`](media-log.md) for footage that actually exists.
- At each meaningful milestone, explicitly record one of: `captured`, `not visually useful`, or `capture failed—recreate if possible`.

### Status and priority legend

- `[x] VERIFIED` — confirmed from code plus a current automated check during the 2026-08-26 audit.
- `[x] HISTORICAL` — supported by a recorded live-game result, but not rerun during this documentation audit.
- `[ ] P0` — blocks trustworthy training or a usable public repository.
- `[ ] P1` — required for the first credible trained-agent release.
- `[ ] P2` — polish, scale, or generalization after the first credible result.
- `[ ] DECISION` — requires an explicit choice recorded in an ADR.
- `[ ] STRETCH` — research direction; keep outside the critical path.

## Audit snapshot

### What is already strong enough to keep

- [x] VERIFIED — The proprietary game directory and generated artifacts are excluded by `.gitignore`.
- [x] VERIFIED — A Gymnasium-style `GeometryDashEnv` implements `reset()` and `step()`.
- [x] VERIFIED — Cube actions are represented as `Discrete(2)`: no-op and jump.
- [x] VERIFIED — RGB observations resize to `160×90` and optional frame stacking preserves order.
- [x] VERIFIED — The current Python 3.13 installation passes all 10 unit tests.
- [x] HISTORICAL — The environment completed a 100-step benchmark at 83.42 ms mean step time / 11.99 decisions per second.
- [x] HISTORICAL — The reset path completed 50 consecutive deaths with zero recorded reset failures.
- [x] HISTORICAL — The capture path held one bounding box and image size across 100 samples.
- [x] HISTORICAL — Non-learning no-op, random-jump, and periodic-jump policies were measured over 10 episodes each.
- [x] VERIFIED — The repository records engineering decisions, learning history, screen-state evidence, environment behavior, and selected media.

### Quality audit of existing project material

| Material | Decision | Why |
| --- | --- | --- |
| `README.md` | Replaced; continue updating with verified milestones | It now exposes engineering status, learning proof, media evidence, limitations, safety/legal scope, and the lack of a clean-install contract. |
| `docs/roadmap.md` | Replaced by this file | The old file mixed stages and phases, duplicated work, and contradicted itself about baseline completion. |
| `docs/learning-log.md` | Keep as historical journal; improve future entries | It contains valuable failure and measurement history. Future experiments need structured, separate reports. |
| `docs/learning/README.md` | New learning source of truth | It defines just-in-time RL modules and what counts as credible GitHub proof of understanding. |
| `docs/environment-api.md` | Keep, then update | It is a useful contract but contains timing assumptions that no longer match the measured decision rate and omits several failure semantics. |
| `docs/screen-state-map.md` | Keep as evidence, not specification | It is based on one episode and cannot establish detector generalization. |
| `docs/montage-plan.md` | New story and capture source of truth | It defines the M00–M22 shot list, capture triggers, technical standard, archive layout, and edit-integrity rules. |
| `docs/media-log.md` | Upgraded as the actual footage catalog | It now distinguishes raw/candidate/selected/published media and records preservation gaps. |
| `docs/decisions/0001-rl-environment-interface.md` | Keep and supersede where needed | The decision is sound, but its open questions now need resolution or links to later ADRs. |
| `pyproject.toml` and `uv.lock` | Replaced `requirements.txt` | Python support, runtime/dev dependencies, package metadata, and the resolved environment now have one source of truth. |
| `src/geometry_dash_env/` | Keep and harden | The prototype works, but configuration, portability, state detection, reward correctness, and package boundaries need work before training. |
| `tests/` | Keep and expand | The synthetic unit tests are fast and useful but do not cover the detector dataset, state machine, training interface, or clean installation. |
| `tools/` | Keep, then refactor into supported CLIs | The tools preserve valuable experiments but duplicate bootstrapping/import logic and do not emit machine-readable results consistently. |

### Known blockers discovered by this audit

- [x] VERIFIED — Recreate `.venv` with locked dependencies on Python 3.13.14; preserve the broken environment locally for recovery.
- [x] VERIFIED — Stop relying on the globally installed Python environment; tests and tools now run through `uv run`.
- [x] VERIFIED — Add an installable package definition and resolved `uv.lock`.
- [ ] P0 — Add CI; no automated GitHub checks currently protect the repository.
- [ ] P0 — Choose and add an open-source license before describing the repository as open source.
- [ ] P0 — Fix the README status: the environment and non-learning baselines exist, but no learning agent or checkpoint exists.
- [ ] P0 — Validate screen-state and progress heuristics on a labeled multi-episode dataset instead of one recorded run.
- [ ] P0 — Add a continuous progress signal or deliberately choose a sparse-reward experiment before serious training.
- [ ] P0 — Define an experiment protocol before comparing learning algorithms.

## Definition of a credible v1

Version 1 is complete only when all statements below are true.

- [ ] A new contributor with Windows and a legitimate Geometry Dash installation can clone, install, configure, and run offline tests from the README.
- [ ] CI installs the package in a clean Windows environment and passes formatting, linting, typing, unit tests, and offline detector tests.
- [ ] The live environment has a documented state machine, bounded failure behavior, and recorded reset/capture reliability results.
- [ ] Observation, action, termination, truncation, and reward contracts are versioned and tested.
- [ ] Every reported experiment can be traced to a config, seed, git commit, environment fingerprint, metrics file, and checkpoint.
- [ ] A trained policy beats the strongest locked non-learning baseline on a predeclared evaluation protocol.
- [ ] The comparison uses multiple independent training seeds and reports variability, not only the best run.
- [ ] A held-out evaluation video and machine-readable results are published without proprietary game binaries.
- [ ] The learning index proves RL understanding through own-word explanations, pre-run predictions, from-scratch exercises, measured results, reflections, and assistance disclosures.
- [ ] The media archive contains traceable baseline, environment, learning, failure/fix, checkpoint-progression, final-comparison, and limitation footage.
- [ ] The README clearly separates verified achievements, current limitations, future plans, and non-affiliation with Geometry Dash/RobTop Games.
- [ ] The repository has a license, contribution guidance, security guidance, citation metadata, and a tagged release.

## Three-track proof matrix

| Build phase | RL concept to learn | GitHub proof | Montage checkpoint |
| --- | --- | --- | --- |
| Foundation | Scientific workflow, reproducibility, MDP vocabulary | L0 project-as-MDP note, clean setup evidence, learning disclosure | M00 origin, M01 human reference, preserve current M05 footage |
| Environment | State versus observation, episodes, terminal/truncated, POMDP | State-machine explanation, contract tests, failure reflection | M03 observations, M04 action, M05 state flow, M06 reset loop, M07 detector failure/fix |
| Reward | Return, discount, sparse/shaped reward, reward hacking | Hand calculations, reward invariants, pre-run reward prediction | M08 progress/reward overlay |
| Representation | CNN input, channel order, memory, temporal information | Representation comparison and tensor tests | M03 raw versus transformed observations |
| Baselines | Policy, exploration, bandits, uncertainty | Epsilon-greedy exercise, strengthened baseline report | M02 matched baseline clips, M09 learning-by-hand insert |
| Algorithm | Values, Bellman/TD, Q-learning, DQN, policy-gradient/PPO trade-offs | Toy implementations, hand updates, algorithm ADR | M10 toy agent learns, M11 first live update |
| Training | Checkpointing, debugging, one-variable experiments | Predictions, traces, failure classification, resume test | M12 first improvement, M13 checkpoints, M14 repeated failure, M15 controlled fix |
| Evaluation | Multiple seeds, held-out tests, confidence, honest claims | Raw episode data, generated analysis, own-word conclusion | M16 milestones, M17 completion, M18 baseline comparison, M20 limitation |
| Robustness | Generalization versus memorization | Robustness matrix and scoped claims | M19 held-out condition |
| Release/story | Reproducibility, scientific communication, teach-back | Learning index, model/data cards, technical walkthrough | M21 teach-back and M22 final hero shot |

---

## Phase 0 — Make the repository reproducible and honest

**Problem:** The prototype works only through an untracked global Python environment, and the public entry point is outdated.

**Acceptance:** A clean Windows clone installs predictably, runs all offline checks, and accurately describes project status.

**Verify:** Follow the README from a clean clone, then run the documented `quality`, `test`, and packaging commands.

### 0.1 Preserve the current evidence before refactoring

- [x] VERIFIED — Tag `prototype-baseline-8d4e496` preserves the pre-refactor prototype at commit `8d4e496` for regression comparisons.
- [x] VERIFIED — Record the Windows edition/build, CPU, GPU, RAM, display scaling, monitor layout, refresh rate, and provenance limits in `docs/experiment-environment.md`.
- [x] VERIFIED — Record CPython `3.13.14`, used by the successful locked test run, in `docs/experiment-environment.md`.
- [ ] P0 — Record the Geometry Dash version from the in-game UI or store; the executable exposes no usable version metadata.
- [ ] P0 — Record window mode, client resolution, VSync/FPS settings, level, character mode, and game speed.
- [x] VERIFIED — Record `ffmpeg 8.1.1-full_build-www.gyan.dev` and video-encoding provenance in `docs/experiment-environment.md`; the episode recorder encoded H.264 while benchmarks do not encode video.
- [x] VERIFIED — Export `docs/dependency-snapshot-20260826.txt` as historical evidence; `uv.lock` remains the dependency source of truth.
- [x] VERIFIED — Back up the selected state-flow video to ignored `media-backups/20260826T113120Z/` outside `artifacts/` before cleanup.
- [x] VERIFIED — Add `docs/media-checksums.sha256` for the milestone video, sidecar metadata, and identical local backup.

### 0.2 Rebuild Python project metadata

- [x] VERIFIED — Choose `>=3.12,<3.14`, pin Python 3.13 by default, and record the reasoning in ADR 0002.
- [x] VERIFIED — Choose `uv` for Python pinning, locking, synchronization, and project commands; record the reasoning in ADR 0002.
- [x] VERIFIED — Add `pyproject.toml` with package metadata, Python requirement, runtime dependencies, and a development dependency group.
- [x] VERIFIED — Remove `requirements.txt` after moving its dependencies into project metadata.
- [x] VERIFIED — Generate `uv.lock` and verify it with `uv lock --check`.
- [x] VERIFIED — Keep the environment package minimal and leave training/experiment dependencies out until their decisions are made.
- [x] VERIFIED — Declare Windows as the live-control platform in package metadata and README.
- [x] VERIFIED — Configure the `src` layout so imports use `geometry_dash_env`, never `src.geometry_dash_env`.
- [x] VERIFIED — Remove library imports from `tools`; move Windows control and screen detection under `src/geometry_dash_env`.
- [ ] P0 — Add supported command-line entry points for capture, benchmark, baseline, train, evaluate, and record operations.

> Evidence note (2026-08-26): `docs/command-surface.md` inventories the implemented capture, benchmark, baseline, and record commands. `train` and `evaluate` remain intentionally absent until the learning protocol exists.
- [x] VERIFIED — Recreate `.venv` from the lock file with Python 3.13.14.
- [x] VERIFIED — Verify dependency consistency with `uv pip check`.
- [x] VERIFIED — Verify `uv run python -c "import geometry_dash_env"` works from the project environment.
- [x] VERIFIED — Build both wheel and source distribution successfully.
- [x] VERIFIED — Install the wheel into an isolated environment and pass an import smoke test.

### 0.3 Add a repeatable developer command surface

- [x] VERIFIED — Choose `uv` as the Windows-friendly task runner and document the canonical PowerShell commands in `docs/developer-commands.md`.
- [ ] P0 — Add commands for `setup`, `format`, `lint`, `typecheck`, `test`, `test-offline`, `test-live`, `benchmark`, `train`, and `evaluate`.
- [ ] P0 — Ensure offline commands never require the game executable or a running game window.
- [ ] P0 — Ensure live commands fail with a short actionable message when Windows, the game path, or the game window is unavailable.
- [ ] P0 — Add `--help` examples and validate every public CLI's exit codes.
- [ ] P1 — Add shell completion only after CLI names and flags stabilize.

### 0.4 Add code-quality gates

- [x] VERIFIED — Select Ruff, Pyright, and Coverage.py; scope is `src/`, `tests/`, and `tools/`, with Win32-only input excluded from the coverage floor.
- [x] VERIFIED — Configure deterministic formatting.
- [x] VERIFIED — Configure lint rules, with narrow documented ignores instead of file-wide suppression.
- [x] VERIFIED — Configure type checking for package code first, then tools and tests.
- [ ] P0 — Add docstring requirements for public APIs and CLI entry points.
- [x] VERIFIED — Add a pre-commit configuration for formatting, linting, whitespace, YAML/TOML validation, and secret detection.
- [x] VERIFIED — Add a branch-aware coverage report with a 60% floor for offline-testable core logic.
- [ ] P0 — Add dead-code and duplicate-code review to the refactor checklist.
- [ ] P0 — Remove stale comments and messages, including reset text that says “pressing R” when the implementation clicks the retry control.

### 0.5 Add continuous integration

- [x] VERIFIED — Add a Windows GitHub Actions workflow for clean installation and offline tests.
- [x] VERIFIED — Add formatting, linting, type checking, unit tests, and package build as separate visible CI steps.
- [x] VERIFIED — Cache dependencies without caching the project environment itself.
- [ ] P0 — Upload test and coverage reports on failure.
- [x] VERIFIED — Run a matrix only for explicitly supported Python versions (3.12 and 3.13).
- [x] VERIFIED — Prove CI never looks for or downloads Geometry Dash.
- [x] VERIFIED — Keep live-game tests out of the default offline test discovery.
- [ ] P0 — Add a scheduled dependency/security audit with actionable failure behavior.
- [ ] P1 — Add a lightweight Linux job for offline modules only after Win32 imports are properly isolated.
- [ ] P1 — Add branch protection instructions requiring the core CI checks.

### 0.6 Replace the README and add repository governance

- [x] VERIFIED — Replace the README headline with a one-sentence, precise project claim.
- [ ] P0 — Add a hero GIF or short result video only when its source experiment is traceable.
- [x] VERIFIED — Add current status: environment and non-learning baseline complete; learning agent not implemented yet.
- [x] VERIFIED — Add a small evidence table that distinguishes current checks, historical live results, and unfinished work.
- [x] VERIFIED — Add a compact architecture/data-flow explanation.
- [x] VERIFIED — Add prerequisites: Windows, legitimate game installation, Python dependencies, and optional ffmpeg.
- [ ] P0 — Add clean installation, game-path configuration, offline test, live smoke test, baseline, training, evaluation, and resume examples.
- [x] VERIFIED — Add a repository map explaining source, tests, tools, learning/media docs, and local artifacts.
- [x] VERIFIED — Add current reproducibility and single-machine evidence limitations.
- [x] VERIFIED — Add a clear safety warning that live control focuses the game and sends keyboard/mouse input.
- [x] VERIFIED — Add legal language: no game executable/assets are distributed, users supply their own copy, and the project is not affiliated with RobTop Games.
- [x] VERIFIED — Add limitations without marketing language: one OS, one level, one mode, heuristic vision, and no trained agent yet.
- [ ] P0 — Add roadmap, contributing, citation, license, and experiment-index links.
- [ ] DECISION — Choose a license compatible with the author's intent; do not guess on the author's behalf.
- [ ] P0 — Add the chosen `LICENSE` file and align README/package metadata with it.
- [ ] P0 — Add `CONTRIBUTING.md` with setup, issue selection, testing, experiment evidence, and PR expectations.
- [ ] P0 — Add `CODE_OF_CONDUCT.md`.
- [ ] P0 — Add `SECURITY.md`, emphasizing that the project sends local input and does not accept game binaries in reports.
- [ ] P0 — Add `CITATION.cff` after author identity and release metadata are confirmed.
- [ ] P1 — Add `CHANGELOG.md` using a consistent release format.
- [ ] P1 — Add issue templates for bugs, environment compatibility, detector failures, and experiment reports.
- [ ] P1 — Add a pull-request template with verification and evidence checkboxes.
- [ ] P1 — Add labels/milestones matching this roadmap.
- [ ] P1 — Enable automated dependency update PRs only after CI is reliable.

### 0.7 Establish learning proof and montage preservation

- [x] VERIFIED — Add `docs/learning/README.md` with a just-in-time RL curriculum and evidence standard.
- [x] VERIFIED — Add `docs/montage-plan.md` with the M00–M22 shot list, capture triggers, metadata, archive, and edit-integrity rules.
- [x] VERIFIED — Upgrade `docs/media-log.md` into an actual-footage catalog with preservation status and a reusable entry template.
- [ ] P0 — Write L0, `docs/learning/00-geometry-dash-as-an-mdp.md`, in the learner's own words before adding an RL library.
- [ ] P0 — Include a pre-study explanation, prediction, project connection, open questions, and AI/resource disclosure in L0.
- [ ] P0 — Draw and commit the Geometry Dash observation → policy → action → next observation/reward loop.
- [ ] P0 — Back up and checksum the existing M05 state-flow video.
- [ ] P0 — Capture M00 project origin and M01 human reference while the project is still early.
- [ ] P0 — Re-record M02 baseline policies after the baseline protocol is locked.
- [ ] P0 — Add sidecar metadata generation to future capture/evaluation tooling.
- [ ] P0 — Add a deliberate media decision field to experiment reports: captured, not visually useful, or capture failed.
- [ ] P0 — Add an assistance disclosure to each learning module so GitHub evidence remains honest.
- [ ] P1 — Record short teach-back clips at major RL modules for possible M09/M21 use.

### Phase 0 exit gate

- [x] VERIFIED — Recreate the project environment from the documented lock workflow; preserve the prior broken environment as a recoverable local backup.
- [x] VERIFIED — Run every offline quality command in the recreated environment with no global packages.
- [x] VERIFIED — Build the package and import its wheel in an isolated environment.
- [ ] P0 — Confirm CI passes on the public repository.
- [ ] P0 — Ask a second person, or use a genuinely clean Windows user/VM, to follow the README without unstated help.
- [ ] P0 — L0 is complete and reviewable as genuine learning evidence.
- [ ] P0 — Existing irreplaceable footage has a checksum, second backup, and privacy/rights review status.

---

## Phase 1 — Harden the live environment contract

**Depends on:** Phase 0 installation and offline test gates.

**Problem:** The current environment is a good single-machine prototype but conflates transition/gameplay states and relies on hard-coded local assumptions.

**Acceptance:** The environment behaves as a versioned state machine and fails safely across known window, reset, timing, and input edge cases.

**Verify:** Offline contract tests plus a versioned live qualification run.

### 1.1 Isolate and configure platform control

- [ ] P0 — Move game discovery, Win32 window control, input dispatch, and screen capture behind explicit interfaces.
- [ ] P0 — Prevent `ctypes.WinDLL` calls at import time on non-Windows platforms.
- [ ] P0 — Replace the hard-coded `Geometry Dash/GeometryDash.exe` assumption with config/CLI discovery while retaining a safe default.
- [ ] P0 — Normalize and validate the configured executable path without logging sensitive parent paths unnecessarily.
- [ ] P0 — Identify the game process/window by more than one robust signal; handle multiple matching windows explicitly.
- [ ] P0 — Reacquire the window handle after game restart or handle invalidation.
- [ ] P0 — Detect minimized, occluded, zero-size, or off-screen client areas and stop safely.
- [ ] P0 — Detect client resolution changes and either rebuild observation state or terminate with a clear reason.
- [ ] P0 — Decide whether moving/resizing the window mid-episode is supported; test the chosen behavior.
- [ ] P0 — Expose capture/input backends through dependency injection for offline tests.
- [ ] P0 — Add an emergency-stop mechanism and document the key combination.
- [ ] P0 — Add a maximum action rate so a bug cannot flood input indefinitely.
- [ ] P0 — Restore the user's cursor only if cursor movement remains necessary for reset.
- [ ] P0 — Prefer a reset input that does not depend on hard-coded screen coordinates; otherwise calibrate and validate normalized coordinates.
- [ ] P0 — Make focus-stealing behavior explicit and opt-in for live commands.
- [ ] P1 — Measure whether the input API drops presses at different game/window states.
- [ ] P1 — Add press-duration configuration and validate a short press across supported machines.

### 1.2 Replace the coarse state classifier with a tested state machine

- [ ] P0 — Define canonical states: `DISCONNECTED`, `MAIN_MENU`, `LEVEL_INFO`, `ATTEMPT_INTRO`, `GAMEPLAY`, `DEATH_ANIMATION`, `RESULTS`, `LEVEL_COMPLETE`, `RESETTING`, and `ERROR`.
- [ ] P0 — Define legal transitions and timeouts for every state.
- [ ] P0 — Separate `ATTEMPT_INTRO` from `GAMEPLAY`; do not expose transition frames as valid initial observations unless deliberately specified.
- [ ] P0 — Detect death close to collision or explicitly document terminal-detection delay.
- [ ] P0 — Detect successful level completion separately from death.
- [ ] P0 — Decide whether pause/menu/focus-loss states truncate, error, or recover; encode the result.
- [ ] P0 — Attach `screen_state`, previous state, transition reason, and detector confidence to diagnostic info.
- [ ] P0 — Ensure normal actions are suppressed outside `GAMEPLAY`.
- [ ] P0 — Ensure reset input is sent only from a validated resettable state.
- [ ] P0 — Add bounded recovery for delayed results, missed clicks, level-info screens, and lost focus.
- [ ] P0 — Fail after a configured recovery budget; never loop forever.
- [ ] P0 — Save a small diagnostic bundle on unexpected state/timeouts: timestamp, recent states, config, and selected frames.
- [ ] P0 — Redact local paths/user data from shareable diagnostics.

### 1.3 Build a labeled screen-state validation dataset

- [ ] P0 — Define an annotation schema with state, level, resolution, window mode, theme/color effects, timestamp, and episode ID.
- [ ] P0 — Collect multiple independent episodes rather than adjacent frames from only one run.
- [ ] P0 — Include every canonical state and difficult transition boundaries.
- [ ] P0 — Include at least two client resolutions and multiple window positions/scales used by the project.
- [ ] P0 — Include negative examples containing bright green, dark overlays, menus, and unrelated desktop content.
- [ ] P0 — Split by episode, not random neighboring frame, to prevent leakage.
- [ ] P0 — Keep detector-development and held-out test episodes separate.
- [ ] P0 — Version annotations and collection metadata.
- [ ] P0 — Decide what visual samples can legally be published; keep non-distributable data local and publish collection scripts/metadata instead.
- [ ] P0 — Add an offline evaluation CLI that emits confusion matrix, per-state precision/recall/F1, and transition latency.
- [ ] P0 — Set minimum acceptable recall for terminal states and maximum false-terminal rate before live qualification.
- [ ] P0 — Add regression fixtures for every detector bug that is fixed.
- [ ] P1 — Have a second labeling pass on ambiguous transition frames and record agreement.

### 1.4 Version and test the Gymnasium contract

- [ ] P0 — Publish observation-contract version, action-contract version, reward-contract version, and environment version in `info` and run metadata.
- [ ] P0 — Decide the canonical image layout (`HWC` or `CHW`) and make wrappers explicit.
- [ ] P0 — Fix frame-stacked shape semantics for the chosen training library; `(stack, H, W, C)` may not be accepted by standard CNN policies.
- [ ] P0 — Validate `observation_space.contains(observation)` on reset and every step in a stress test.
- [ ] P0 — Define whether the terminal observation is gameplay, death animation, or results; test it.
- [ ] P0 — Define and test `terminated` for death and completion.
- [ ] P0 — Define and test `truncated` for time limit, focus loss, invalid state, and operator stop.
- [ ] P0 — Use structured termination/truncation reasons in `info`.
- [ ] P0 — Correct the documented duration of `max_steps=900`; measured 11.99 decisions/sec implies about 75 seconds, not 60.
- [ ] P0 — Decide how `reset(seed=...)` is described because it cannot seed Geometry Dash itself.
- [ ] P0 — Either implement supported `reset(options=...)` behavior or document/reject unused options.
- [ ] P0 — Make `close()` safe to call multiple times.
- [ ] P0 — Support context-manager cleanup or document the required lifecycle.
- [ ] P0 — Run Gymnasium's environment checker on an offline/fake backend and resolve applicable warnings.
- [ ] P0 — Add tests for invalid constructor values and invalid action types/values.
- [ ] P0 — Add tests for time-limit truncation, post-terminal step rejection, double reset, double close, and reset after truncation.
- [ ] P0 — Add tests for results reset, transition timeout, unknown state, main menu, focus loss, window disappearance, and bbox change.
- [ ] P0 — Add tests for frame-stack reset, buffer independence, dtype, ordering, and no accidental aliasing.

### 1.5 Requalify timing, capture, and reset reliability

- [ ] P0 — Define warm-up frames and exclude them consistently from performance metrics.
- [ ] P0 — Record mean, median, p95, p99, min, max, and missed-deadline rate rather than mean alone.
- [ ] P0 — Separate capture, state detection, observation transform, input, waiting, reset, and total decision time.
- [ ] P0 — Measure actual captured-frame intervals and action-to-visible-effect latency.
- [ ] P0 — Measure performance with each candidate observation representation and stack depth.
- [ ] P0 — Run at least 1,000 live steps without silent invalid observations.
- [ ] P0 — Run at least 100 consecutive death/reset cycles with zero unhandled failures for v1.
- [ ] P0 — Intentionally move and resize the window during a qualification run if that behavior is supported.
- [ ] P0 — Intentionally lose focus and verify the documented safe behavior.
- [ ] P0 — Verify memory use remains bounded across a long run.
- [ ] P0 — Verify all input keys are released after exceptions and interruption.
- [ ] P0 — Store qualification results as machine-readable JSON plus a concise Markdown report.
- [ ] P0 — Link each qualification report to its config, git SHA, system fingerprint, and selected diagnostic media.

### Phase 1 exit gate

- [ ] P0 — Offline detector/state-machine metrics meet the predeclared thresholds on held-out episodes.
- [ ] P0 — All environment contract tests pass in CI without the game.
- [ ] P0 — Live qualification passes the 1,000-step and 100-reset gates on the reference setup.
- [ ] P0 — Environment API documentation matches observed behavior exactly.
- [ ] P0 — Record an ADR accepting environment contract v1 and listing remaining limitations.

---

## Phase 2 — Establish trustworthy progress and reward signals

**Depends on:** Phase 1 state correctness.

**Problem:** The current terminal result estimate is sparse and calibrated on too little evidence; unvalidated shaping can teach the wrong behavior.

**Acceptance:** Progress and terminal outcomes are measured with known error, and the selected reward is covered by invariants and ablations.

**Verify:** Offline labeled evaluation plus live episode consistency checks.

### 2.1 Define progress ground truth

- [ ] DECISION — Choose the authoritative progress definition: in-game percentage, level coordinate, progress-bar fill, or a calibrated proxy.
- [ ] P0 — Specify expected range, resolution, monotonicity, latency, and unavailable-value behavior.
- [ ] P0 — Collect paired gameplay frames and result-screen percentages across early, middle, late, death, and completion cases.
- [ ] P0 — Validate the current results progress estimator against manually recorded ground truth.
- [ ] P0 — Report mean absolute error, worst-case error, bias, and missing-value rate.
- [ ] P0 — Add fixtures for UI themes/resolutions where green heuristics may fail.
- [ ] P0 — Treat unreadable progress as missing data, not a fabricated zero.
- [ ] P0 — Version progress-detector thresholds/configuration.

### 2.2 Implement per-step progress safely

- [ ] P0 — Prototype at least two measurement methods offline before integrating reward.
- [ ] P0 — Measure progress only in valid gameplay states.
- [ ] P0 — Filter jitter without hiding real backward/forward anomalies.
- [ ] P0 — Clamp impossible jumps and emit a diagnostic counter.
- [ ] P0 — Preserve raw and filtered progress in run logs.
- [ ] P0 — Compute `progress_delta` from newly achieved forward progress, not repeatedly from absolute progress.
- [ ] P0 — Decide how checkpoints/respawns or level restarts reset progress state.
- [ ] P0 — Test zero movement, normal movement, detector jitter, death transition, reset, completion, and missing measurement.
- [ ] P0 — Compare summed progress deltas with terminal result progress over complete episodes.

### 2.3 Specify reward versions and invariants

- [ ] DECISION — Lock a sparse terminal reward baseline before adding shaping.
- [ ] P0 — Define distinct values/terms for forward progress, survival if used, death, completion, truncation, and invalid-state termination.
- [ ] P0 — Keep each reward component separately visible in `info` and logs.
- [ ] P0 — Ensure standing still cannot accumulate meaningful progress reward.
- [ ] P0 — Ensure repeating the same frame cannot accumulate progress reward.
- [ ] P0 — Ensure reset/transition UI cannot generate progress reward.
- [ ] P0 — Ensure completion is always better than dying at the same measured progress.
- [ ] P0 — Bound per-step and per-episode reward magnitudes.
- [ ] P0 — Define behavior when progress is unavailable.
- [ ] P0 — Add unit/property tests for all reward invariants.
- [ ] P0 — Version every reward change and prevent incomparable runs from sharing the same result table.
- [ ] P1 — Compare sparse, progress-only, progress-plus-death, and progress-plus-small-survival rewards under one protocol.
- [ ] P1 — Reject shaping that raises training reward without raising evaluation progress/completion.

### Phase 2 exit gate

- [ ] P0 — Publish detector error and missing-rate measurements on held-out data.
- [ ] P0 — Publish reward contract v1 with examples and invariants.
- [ ] P0 — Pass all reward regression tests.
- [ ] P0 — Manually review reward-component traces for representative successful and failed episodes.
- [ ] P0 — Record an ADR selecting the first training reward and rejected alternatives.

---

## Phase 3 — Select the observation and action representation

**Depends on:** Reliable state/progress labels from Phases 1–2.

**Problem:** RGB `160×90` plus optional stacking is a baseline, not yet an evidence-based training representation.

**Acceptance:** The smallest representation that preserves task-relevant information and meets latency/memory limits is selected through a fixed comparison.

**Verify:** Offline benchmark report plus an online smoke test using the exact training wrapper.

### 3.1 Build a replayable observation dataset

- [ ] P0 — Record timestamped frames, actions, state labels, progress, reward components, terminal flags, and episode IDs.
- [ ] P0 — Record original capture geometry and transform configuration.
- [ ] P0 — Use a schema with an explicit version and validation command.
- [ ] P0 — Detect incomplete/corrupt episodes and exclude them with recorded reasons.
- [ ] P0 — Split train/validation/test by whole episode.
- [ ] P0 — Prevent later frames from the same attempt leaking across splits.
- [ ] P0 — Record collection policy and seed where applicable.
- [ ] P0 — Store checksums and a manifest without committing large/proprietary artifacts to git.
- [ ] P0 — Publish a data card describing source, scope, licensing constraints, biases, and intended use.
- [ ] P1 — Add a small synthetic or redistribution-safe fixture dataset for CI.

### 3.2 Compare observation variants

- [ ] P0 — Lock the comparison dataset and metrics before tuning transforms.
- [ ] P0 — Benchmark RGB versus grayscale.
- [ ] P0 — Benchmark full frame versus a gameplay crop that removes irrelevant borders/UI.
- [ ] P0 — Benchmark at least two spatial resolutions.
- [ ] P0 — Benchmark frame stack depths `1`, `2`, and `4` or justify a smaller set.
- [ ] P0 — Benchmark frame differencing or optical-flow-like motion only as an explicit candidate.
- [ ] P0 — Record transform latency, observation bytes, replay-buffer memory, and model input shape.
- [ ] P0 — Visualize transformed observations and stacks to catch crop/order/channel bugs.
- [ ] P0 — Check that the player, near obstacles, ground, and motion remain distinguishable.
- [ ] P0 — Use a small fixed downstream proxy task or short agent smoke test, not visual preference alone.
- [ ] P0 — Select one observation v1 and freeze its config.
- [ ] P0 — Add golden-image transform tests and shape/dtype/range tests.
- [ ] P1 — Keep object detection/structured features as a documented alternative, not an unmeasured assumption.

### 3.3 Validate action semantics

- [x] VERIFIED — Initial cube action set is `0=noop`, `1=jump`.
- [ ] P0 — Measure action-to-visible-jump latency and its variance.
- [ ] P0 — Validate how one short press behaves at every supported frame-skip value.
- [ ] P0 — Decide whether an action is sent once per decision or held/repeated across skipped frames; document and test it.
- [ ] P0 — Detect and prevent stuck keys after interruption.
- [ ] P0 — Log requested action, dispatched action, dispatch timestamp, and any suppressed action.
- [ ] P1 — Measure whether action history belongs in the observation.
- [ ] P2 — Add explicit press/hold/release only when a target mode requires it.
- [ ] P2 — Version mode-specific action spaces; do not silently expand `Discrete(2)`.

### Phase 3 exit gate

- [ ] P0 — Publish the observation comparison table and selection rationale.
- [ ] P0 — The chosen wrapper produces the exact tensor layout expected by the training library.
- [ ] P0 — Transform latency fits inside the live decision budget with acceptable p95/p99.
- [ ] P0 — Action timing is documented and passes a live repeatability check.
- [ ] P0 — Record an ADR accepting observation/action contract v1.

---

## Phase 4 — Build experiment and baseline infrastructure

**Depends on:** Frozen environment/reward/observation contracts.

**Problem:** The existing 10-episode baselines are a useful smoke test but too small and insufficiently structured for scientific comparison.

**Acceptance:** Every run is reproducible, resumable, comparable, and automatically summarized.

**Verify:** Re-run a baseline from its saved config and reproduce the stored metrics within declared tolerance.

### 4.1 Define the experiment protocol before training

- [ ] P0 — Write the primary research question for v1 in one sentence.
- [ ] P0 — Predeclare the primary metric: completion rate first, then progress/AUC or another justified fallback.
- [ ] P0 — Define secondary metrics: median progress, best progress, episode length, deaths, truncations, reset failures, wall time, and environment steps.
- [ ] P0 — Define training budget in environment steps and wall-clock time.
- [ ] P0 — Define evaluation episode count and independent seed count.
- [ ] P0 — Define checkpoint selection without using held-out evaluation results repeatedly.
- [ ] P0 — Separate training, validation/model-selection, and final held-out evaluation episodes.
- [ ] P0 — Define failure/exclusion rules before seeing results.
- [ ] P0 — Define what constitutes “beats baseline” including uncertainty/tie handling.
- [ ] P0 — Freeze a reference environment config and baseline protocol ID.
- [ ] P0 — Document determinism limits: game physics may be deterministic, but capture/input scheduling is not fully seed-controlled.

### 4.2 Standardize run configuration and identity

- [ ] P0 — Add versioned config files for environment, observation, reward, algorithm, training, evaluation, recording, and system settings.
- [ ] P0 — Validate configs and reject unknown keys.
- [ ] P0 — Resolve config inheritance/overrides into one saved immutable run config.
- [ ] P0 — Generate a unique run ID and output directory before interaction begins.
- [ ] P0 — Save start/end UTC, git SHA, dirty-tree flag, command, Python/package versions, OS, hardware, and config hash.
- [ ] P0 — Save environment/observation/action/reward contract versions.
- [ ] P0 — Save seed values for library RNGs and the policy.
- [ ] P0 — Refuse an official comparison run from a dirty tree unless explicitly marked exploratory.
- [ ] P0 — Add run states: created, running, interrupted, failed, completed, evaluated.
- [ ] P0 — Write metadata atomically so interruption does not corrupt the run record.

### 4.3 Standardize metrics and artifacts

- [ ] P0 — Emit per-step or sampled telemetry to a machine-readable format with a documented schema.
- [ ] P0 — Emit one per-episode table with return, length, progress, outcome, timing, reset result, and checkpoint ID.
- [ ] P0 — Emit a run summary JSON and human-readable Markdown report.
- [ ] P0 — Record rolling metrics without replacing raw data.
- [ ] P0 — Record reward components separately.
- [ ] P0 — Record detector confidence/errors and missed deadlines.
- [ ] P0 — Save checkpoints atomically with model, optimizer, scheduler, normalization, replay-buffer state if feasible, and step counters.
- [ ] P0 — Retain `best`, `latest`, periodic, and final checkpoints according to a documented policy.
- [ ] P0 — Verify checkpoint loading immediately after saving.
- [ ] P0 — Support resume without resetting step counters or overwriting prior metrics.
- [ ] P0 — Record why a run stopped: budget, completion, operator stop, exception, or environment failure.
- [ ] P0 — Add disk-space checks and artifact retention rules.
- [ ] P1 — Integrate an experiment tracker only if local files remain the source of truth or are exportable.

### 4.4 Strengthen non-learning baselines

- [x] HISTORICAL — Always-no-op, random-jump, and periodic-jump policies have initial 10-episode measurements.
- [ ] P0 — Move baseline policies into importable, unit-tested modules.
- [ ] P0 — Add tests for action sequences and seed behavior.
- [ ] P0 — Use the same locked environment/reward/observation contract as learning agents.
- [ ] P0 — Run enough episodes to report stable estimates and uncertainty.
- [ ] P0 — Evaluate multiple random seeds rather than one random action stream.
- [ ] P0 — Sweep periodic intervals on validation episodes only, then lock the best periodic baseline.
- [ ] P0 — Add a simple observation-based heuristic baseline if it can be specified without learning.
- [ ] P0 — Report confidence intervals or bootstrap intervals for key metrics.
- [ ] P0 — Preserve episode-level results, not only aggregate output copied into Markdown.
- [ ] P0 — Re-run the locked baseline whenever the environment/reward/observation version changes.
- [ ] P0 — Do not compare new agents against the old 10-episode table after a contract change.

### 4.5 Add failure-safe long-run behavior

- [ ] P0 — Catch interruption and save a recoverable checkpoint/metadata state.
- [ ] P0 — Stop safely on repeated reset, capture, detector, focus, or disk failures.
- [ ] P0 — Add a configurable consecutive-failure budget.
- [ ] P0 — Release keys and close capture resources on every exit path.
- [ ] P0 — Keep a bounded ring buffer of recent diagnostic frames rather than unbounded capture.
- [ ] P0 — Save the ring buffer only on milestone/failure events.
- [ ] P0 — Add a heartbeat/status line that shows step, episode, progress, speed, ETA, and last error without excessive logs.
- [ ] P1 — Add an unattended dry run long enough to expose file-handle, memory, and log-growth issues.

### Phase 4 exit gate

- [ ] P0 — A baseline run can be launched solely from a committed config.
- [ ] P0 — The run produces validated config, metadata, episode data, summary, and selected media.
- [ ] P0 — An interrupted run resumes without metric/checkpoint corruption.
- [ ] P0 — The strengthened baseline report includes uncertainty and a protocol/version identifier.
- [ ] P0 — The experiment protocol is frozen before the first algorithm comparison.

---

## Phase 5 — Select and smoke-test the first learning algorithm

**Depends on:** Phase 4 locked protocol and run infrastructure.

**Problem:** Choosing PPO, DQN, or another algorithm by popularity would hide constraints imposed by a single slow live environment, pixel inputs, sparse rewards, and limited samples.

**Acceptance:** One algorithm is selected through documented constraints and survives correctness smoke tests before expensive training.

**Verify:** The agent collects transitions, updates parameters, saves/loads, and improves on a tiny controlled sanity task.

### 5.1 Write the algorithm decision matrix

- [ ] P0 — Measure achievable live samples per hour including resets.
- [ ] P0 — Estimate replay-buffer size and RAM for the selected observation format.
- [ ] P0 — List requirements: discrete actions, pixel input, single environment, sample efficiency, checkpoint/resume, and Windows/CUDA support.
- [ ] P0 — Compare at least one off-policy candidate and one on-policy candidate on those constraints.
- [ ] P0 — Verify the chosen library supports the exact observation space/tensor layout.
- [ ] P0 — Verify the chosen library and deep-learning backend support the locked Python version.
- [ ] P0 — Record license compatibility for new dependencies.
- [ ] P0 — Decide whether to begin from pixels, structured features, or demonstrations; keep the choice aligned with the research claim.
- [ ] P0 — Record the selected algorithm and rejected alternatives in an ADR.

### 5.2 Build training-interface tests before live training

- [ ] P0 — Add a fake/replay environment with the same spaces for fast training tests.
- [ ] P0 — Run the selected algorithm's environment checker/wrapper validation.
- [ ] P0 — Assert model input tensor shape, dtype, range, channel order, device, and batch shape.
- [ ] P0 — Assert sampled actions belong to the environment action space.
- [ ] P0 — Assert terminal/truncated transitions are inserted correctly into rollout/replay storage.
- [ ] P0 — Assert reward and observation normalization state is saved/restored if used.
- [ ] P0 — Assert one training update changes model parameters and produces finite losses.
- [ ] P0 — Detect NaN/Inf observations, rewards, gradients, losses, and parameters.
- [ ] P0 — Verify checkpoint round-trip produces identical deterministic actions on fixed observations.
- [ ] P0 — Verify resume restores global step, schedule position, RNG state where supported, and buffer state where required.
- [ ] P0 — Add a tiny synthetic task the algorithm must learn; fail fast if it cannot.

### 5.3 Lock the first smoke-test configuration

- [ ] P0 — Start with the smallest model that can process the chosen observation.
- [ ] P0 — Record optimizer, learning rate, batch size, discount, exploration/entropy settings, update frequency, target/GAE settings, and gradient clipping as applicable.
- [ ] P0 — Justify replay-buffer capacity and warm-up for off-policy training.
- [ ] P0 — Justify rollout length and batch divisibility for on-policy training.
- [ ] P0 — Set deterministic evaluation and disable training exploration/noise there.
- [ ] P0 — Set a very short live smoke budget with frequent diagnostics.
- [ ] P0 — Disable automatic hyperparameter sweeps until a single end-to-end run is trustworthy.

### 5.4 Run live learning smoke tests

- [ ] P0 — Verify observations visibly change and actions are not constant because of a wrapper bug.
- [ ] P0 — Verify transitions, rewards, terminals, and resets appear correctly in logs.
- [ ] P0 — Verify training updates occur at the intended cadence.
- [ ] P0 — Verify environment speed remains within the qualified budget while training.
- [ ] P0 — Verify CPU/GPU utilization and memory are stable.
- [ ] P0 — Verify checkpoints and evaluation callbacks do not steal focus or break capture timing.
- [ ] P0 — Run a checkpoint save/load/resume during the smoke test.
- [ ] P0 — Review a short action/progress/reward trace and matching video manually.
- [ ] P0 — Classify every failure as environment, detector, reward, wrapper, algorithm, or infrastructure before changing hyperparameters.

### Phase 5 exit gate

- [ ] P0 — Synthetic sanity task is learned reliably.
- [ ] P0 — Live smoke test completes its budget without environment or checkpoint corruption.
- [ ] P0 — Losses/gradients/values remain finite and actions are correctly dispatched.
- [ ] P0 — A resumed run is behaviorally consistent with its pre-interruption state.
- [ ] P0 — The algorithm ADR and smoke-test report are committed before full training.

---

## Phase 6 — Run the first credible training experiment

**Depends on:** All Phase 5 gates.

**Problem:** A best-looking run is not evidence; training needs locked budgets, multiple seeds, validation, and failure accounting.

**Acceptance:** A predeclared multi-seed experiment completes, all runs are traceable, and results are evaluated against the locked baseline.

**Verify:** Experiment manifest is complete and the aggregation script reproduces all published tables/plots.

### 6.1 Preflight

- [ ] P0 — Freeze code, config, protocol, and dependency lock for the experiment batch.
- [ ] P0 — Confirm git tree is clean and record the commit SHA.
- [ ] P0 — Confirm disk space for checkpoints, telemetry, and selected videos.
- [ ] P0 — Confirm no OS updates, notifications, overlays, or power settings will interrupt the game.
- [ ] P0 — Confirm the game starts at the correct level/mode/settings.
- [ ] P0 — Run a short environment qualification immediately before the batch.
- [ ] P0 — Define run seeds and order before starting.
- [ ] P0 — Define stop/abort criteria for repeated environment failures, divergence, or no progress.
- [ ] P0 — Create the experiment manifest before the first run.

### 6.2 Execute without hidden tuning

- [ ] P0 — Run the planned independent seeds with identical budgets/config except seed.
- [ ] P0 — Do not change hyperparameters mid-batch.
- [ ] P0 — Record all failed/interrupted runs and their causes.
- [ ] P0 — Resume only according to the predeclared policy.
- [ ] P0 — Run periodic validation using fixed validation conditions.
- [ ] P0 — Save periodic/latest/best/final checkpoints under the locked selection rule.
- [ ] P0 — Save representative failure, median, and breakthrough media—not only the best-looking attempt.
- [ ] P0 — Monitor environment health separately from learning metrics.
- [ ] P0 — Preserve raw run data before aggregation.

### 6.3 Analyze the batch

- [ ] P0 — Aggregate all planned seeds, including valid weak runs.
- [ ] P0 — Report environment steps and wall-clock time to each milestone.
- [ ] P0 — Plot training and validation metrics with variability bands.
- [ ] P0 — Compare against locked baselines using the same environment contract and evaluation protocol.
- [ ] P0 — Report mean, median, spread, confidence intervals, and individual seed results.
- [ ] P0 — Report completion rate, progress distribution, failure modes, reset failures, and detector errors.
- [ ] P0 — Check whether reward increased without progress/completion improving.
- [ ] P0 — Check for policy collapse to always-jump/no-op/timing loops.
- [ ] P0 — Inspect behavior around repeated failure locations.
- [ ] P0 — Document negative or inconclusive outcomes honestly.
- [ ] P0 — Generate tables/plots from scripts, not hand-copied values.
- [ ] P0 — Make generated figures include units, sample counts, protocol ID, and readable legends.

### Phase 6 exit gate

- [ ] P0 — Every planned run has a final state and explanation.
- [ ] P0 — Aggregation reproduces results from raw data.
- [ ] P0 — The agent either meets the predeclared baseline-beating criterion or the report clearly says it did not.
- [ ] P0 — The conclusion identifies the next highest-evidence change, not a bundle of guesses.
- [ ] P0 — A model card draft records intended use, training data/interaction, metrics, limitations, and safety considerations.

---

## Phase 7 — Iterate scientifically

**Depends on:** A complete Phase 6 result, successful or not.

**Problem:** Changing observation, reward, architecture, and hyperparameters together destroys causal understanding.

**Acceptance:** Each iteration states one main hypothesis, preserves comparability, and updates the decision record.

**Verify:** Each experiment report links parent run, single main change, outcome, and next decision.

### 7.1 Diagnose before changing anything

- [ ] P1 — Categorize the dominant limitation: state detection, progress/reward, observation, action timing, exploration, optimization, capacity, sample throughput, or evaluation noise.
- [ ] P1 — Support the diagnosis with traces, videos, metrics, or ablations.
- [ ] P1 — Identify the earliest step where the observed behavior diverges from expectation.
- [ ] P1 — Write a falsifiable hypothesis and expected metric change.
- [ ] P1 — Define the smallest experiment that can reject the hypothesis.

### 7.2 Controlled experiment rules

- [ ] P1 — Change one principal factor per experiment.
- [ ] P1 — Keep protocol, evaluation, and unrelated config fixed.
- [ ] P1 — Assign a new contract version if observation/action/reward/environment semantics change.
- [ ] P1 — Re-run baselines after any contract change.
- [ ] P1 — Use validation results for selection and reserve held-out evaluation for meaningful milestones.
- [ ] P1 — Record all attempted configurations, including failed runs.
- [ ] P1 — Correct for multiple comparisons when interpreting large sweeps.
- [ ] P1 — Promote a change only when improvement is repeatable across seeds or clearly labeled preliminary.

### 7.3 Candidate ablations, ordered by evidence

- [ ] P1 — Reward: sparse terminal versus validated progress delta.
- [ ] P1 — Observation: grayscale versus RGB.
- [ ] P1 — Observation: full frame versus crop.
- [ ] P1 — Temporal input: one frame versus selected stack depth.
- [ ] P1 — Decision frequency/frame skip.
- [ ] P1 — Network capacity after input/reward correctness is established.
- [ ] P1 — Learning rate and exploration/entropy schedules.
- [ ] P1 — Replay/rollout settings appropriate to the selected algorithm.
- [ ] P1 — Demonstration-assisted initialization only as a separately labeled method.
- [ ] P2 — Structured player/obstacle features as an explicit alternate research track.

### 7.4 Maintain an experiment registry

- [ ] P1 — Give every experiment a stable ID, title, hypothesis, parent, status, and owner.
- [ ] P1 — Maintain an index linking config, run directories, reports, plots, checkpoints, and media.
- [ ] P1 — Mark results as exploratory, validation, or final evaluation.
- [ ] P1 — Record decisions: adopt, reject, retry, or inconclusive.
- [ ] P1 — Keep a compact leaderboard with protocol/contract versions so incomparable runs are never ranked together.
- [ ] P1 — Archive large artifacts in a durable location and publish checksums/links, not binaries in git.

---

## Phase 8 — Evaluate robustness and generalization

**Depends on:** At least one agent reliably beats the locked baseline on the training condition.

**Problem:** Memorizing one deterministic attempt timing pattern is not the same as learning a robust visual control policy.

**Acceptance:** The policy is tested on predeclared perturbations and held-out conditions, with failures reported.

**Verify:** A robustness matrix generated from episode-level data.

### 8.1 Separate evaluation from training

- [ ] P1 — Load a frozen checkpoint without optimizer updates.
- [ ] P1 — Disable exploration/noise unless a stochastic-policy protocol explicitly samples it.
- [ ] P1 — Use held-out episodes/conditions not used for checkpoint selection.
- [ ] P1 — Lock evaluation seeds/order/config and record them.
- [ ] P1 — Record evaluation video independently from training video.
- [ ] P1 — Repeat evaluation enough times to estimate uncertainty.

### 8.2 Test robustness within the original scope

- [ ] P1 — Repeat after game restart.
- [ ] P1 — Repeat after machine restart.
- [ ] P1 — Test supported window positions and resolutions.
- [ ] P1 — Test small capture/action timing jitter.
- [ ] P1 — Test occasional focus recovery if claimed as supported.
- [ ] P1 — Test different cosmetic character choices/background variations if they affect pixels.
- [ ] P1 — Test from fresh attempt transitions, not only a perfectly staged initial state.
- [ ] P1 — Report detector/reset failures separately from policy failures.

### 8.3 Test generalization claims conservatively

- [ ] P2 — Define exactly which new level/mode is held out and why.
- [ ] P2 — Verify the environment, state detector, progress signal, and action space support that condition before blaming the policy.
- [ ] P2 — Evaluate zero-shot performance before any fine-tuning.
- [ ] P2 — Report fine-tuning data/budget separately from original training.
- [ ] P2 — Do not claim “plays Geometry Dash” from success on one level and cube mode.
- [ ] P2 — Expand action semantics before ship, wave, UFO, ball, spider, or robot evaluation.
- [ ] P2 — Add mode/level metadata to every episode and result table.

### Phase 8 exit gate

- [ ] P1 — Robustness results include all predeclared conditions and failures.
- [ ] P1 — Claims in the README match the narrowest evidence-supported scope.
- [ ] P1 — A frozen evaluation bundle contains checkpoint ID, config, raw results, summary, and representative video.

---

## Phase 9 — Publish a world-class documentation set

**Depends on:** Documentation should evolve throughout the project; final result sections depend on Phases 6–8.

**Problem:** A learning log alone does not let users reproduce, audit, or understand the system.

**Acceptance:** Documentation serves newcomers, contributors, reviewers, and researchers without duplicating or contradicting itself.

**Verify:** Link check, clean-clone walkthrough, claim/evidence review, and documentation ownership table.

### 9.1 Define document ownership

- [ ] P0 — Add `docs/index.md` as the documentation map.
- [ ] P0 — Assign one source of truth for setup, configuration, environment API, experiment protocol, results, roadmap, and troubleshooting.
- [ ] P0 — Replace duplicated explanations with links.
- [ ] P0 — Add “last verified” and contract/version context to operational documents.
- [ ] P0 — Add a documentation link checker to CI.
- [ ] P0 — Add a stale-doc review checkbox to PRs that change public behavior.

### 9.2 Core technical documents

- [ ] P0 — Add `docs/setup-windows.md` with clean installation and game configuration.
- [ ] P0 — Add `docs/architecture.md` covering control, capture, state, observation, reward, agent, logging, and artifact flow.
- [ ] P0 — Update `docs/environment-api.md` to the accepted contract version.
- [ ] P0 — Add `docs/configuration.md` with every setting, default, unit, allowed range, and compatibility constraint.
- [ ] P0 — Add `docs/experiment-protocol.md` with baseline/training/evaluation rules.
- [ ] P0 — Add `docs/reproducibility.md` with seeds, determinism limits, hardware, locks, artifact retrieval, and expected tolerances.
- [ ] P0 — Add `docs/troubleshooting.md` for window discovery, focus, DPI, capture, reset, ffmpeg, CUDA, performance, and checkpoint issues.
- [ ] P0 — Add `docs/safety-and-legal.md` for input control, emergency stop, game ownership, non-affiliation, artifacts, privacy, and responsible claims.
- [ ] P1 — Add `docs/model-card.md` for the first released checkpoint.
- [ ] P1 — Add `docs/data-card.md` for recorded/annotated observations.
- [ ] P1 — Add `docs/results.md` generated or verified from experiment summaries.

### 9.3 Decision and learning records

- [ ] P0 — Resolve or supersede ADR 0001's open questions with links to evidence.
- [ ] P0 — Add ADRs for environment contract, observation/action representation, progress/reward, algorithm, dependency workflow, and artifact storage.
- [ ] P0 — Use ADR statuses: proposed, accepted, superseded, or rejected.
- [ ] P0 — Never edit away the historical reasoning of an accepted ADR; supersede it.
- [ ] P0 — Keep `learning-log.md` chronological and append-only except factual corrections.
- [ ] P0 — Add an experiment report template with hypothesis, protocol, config, results, failure analysis, decision, and next step.
- [ ] P0 — Add a bug/failure report template with reproduction, expected/actual, evidence, root cause, fix, and regression test.
- [ ] P0 — Link learning-log milestones to commits, ADRs, experiment IDs, and media where available.

### 9.4 Results presentation

- [ ] P1 — Lead with the strongest verified result and exact scope.
- [ ] P1 — Include non-learning baselines beside trained-agent results.
- [ ] P1 — Show central tendency and variability, not only best progress.
- [ ] P1 — Label training curves versus held-out evaluation metrics.
- [ ] P1 — Include environment steps, wall time, hardware, seeds, and protocol ID.
- [ ] P1 — Show representative failure behavior as well as success.
- [ ] P1 — Link every figure/table/video to its generating run or script.
- [ ] P1 — Use accessible colors, labels, captions, and alt text.
- [ ] P1 — Compress media for GitHub without destroying readability.
- [ ] P1 — Keep raw high-quality media outside git and publish durable links/checksums.

### 9.5 Review every public claim

- [ ] P0 — Search README/docs/release text for “learns,” “solves,” “generalizes,” “real time,” “reproducible,” and “state of the art.”
- [ ] P0 — Attach evidence and scope to each retained claim.
- [ ] P0 — Replace unsupported claims with measured facts.
- [ ] P0 — State when results come from one machine or one level.
- [ ] P0 — State which live tests cannot run in CI.
- [ ] P0 — State that no proprietary executable or game asset is included.
- [ ] P0 — Check all commands, paths, anchors, tables, and relative links from a clean clone.

---

## Phase 10 — Release and maintain the project

**Depends on:** A credible trained result and complete v1 documentation.

**Problem:** A commit on `main` is not a reproducible release.

**Acceptance:** Source, checkpoint, config, results, and documentation are versioned together with integrity and maintenance expectations.

**Verify:** Download release assets into a clean environment and reproduce the documented evaluation.

### 10.1 Prepare release artifacts

- [ ] P1 — Choose semantic version and release scope.
- [ ] P1 — Freeze source, lock file, configs, protocol, docs, and model card.
- [ ] P1 — Build and test wheel/source distribution.
- [ ] P1 — Export the selected checkpoint in the documented loadable format.
- [ ] P1 — Include checkpoint checksum, size, framework/library version, contract versions, and training run ID.
- [ ] P1 — Include evaluation raw results and generated summary.
- [ ] P1 — Include a small representative demo, not proprietary game files.
- [ ] P1 — Generate release notes with achievements, exact scope, breaking changes, limitations, and upgrade steps.
- [ ] P1 — Update changelog and citation version/date.
- [ ] P1 — Create an immutable git tag from a clean, CI-passing commit.

### 10.2 Verify release reproducibility

- [ ] P1 — Download assets from their public location; do not use the original local copies.
- [ ] P1 — Verify every published checksum.
- [ ] P1 — Install from the release artifact in a clean environment.
- [ ] P1 — Load the released checkpoint and run offline inference on a fixture.
- [ ] P1 — Run the documented live evaluation on the reference setup.
- [ ] P1 — Reproduce the published summary within declared tolerance.
- [ ] P1 — Test all README release links and commands.

### 10.3 Maintenance policy

- [ ] P1 — Define supported Python, Windows, game, and dependency versions.
- [ ] P1 — Define what counts as a breaking environment/model-contract change.
- [ ] P1 — Define deprecation and migration policy for configs/checkpoints.
- [ ] P1 — Define issue triage labels and expected response scope.
- [ ] P1 — Define how detector failures are reported without uploading copyrighted or sensitive content publicly.
- [ ] P1 — Schedule periodic dependency, CI, documentation, and link checks.
- [ ] P1 — Archive or mark the project clearly if it is no longer maintained.

---

## Phase 11 — Demo and portfolio story

**Depends on:** Use prototype media early, but make final claims only after evaluation.

**Problem:** A strong engineering project can look weak if the demo hides the problem, evidence, or failures.

**Acceptance:** A short viewer can understand the challenge, system, breakthrough, quantitative result, and limitations.

**Verify:** Every scene and number maps to a documented artifact/run.

- [ ] P1 — Define the single “wow moment” for the final project page.
- [ ] P1 — Draft a 30–60 second story: problem → perception/control loop → training → result → limitation.
- [ ] P1 — Use the existing state-flow recording to explain environment engineering if its archive/checksum is secure.
- [ ] P1 — Capture synchronized overlays for action, state, progress, reward, and policy confidence only if they remain legible.
- [ ] P1 — Capture comparable baseline and trained-agent clips under the same conditions.
- [ ] P1 — Include one failure clip to demonstrate honest analysis.
- [ ] P1 — Add captions and avoid copyrighted music.
- [ ] P1 — Blur/redact unrelated desktop content, paths, usernames, notifications, and secrets.
- [ ] P1 — Verify media playback on GitHub and mobile.
- [ ] P1 — Link the demo to repo, release, model card, results, and reproduction guide.
- [ ] P1 — Prepare a concise portfolio description and a deeper technical write-up without changing claims between them.

---

## Phase 12 — Stretch research directions

These items are deliberately outside v1. Start one only after the critical path is healthy and record a new research question/protocol.

- [ ] STRETCH — Learn from human demonstrations, then fine-tune with RL.
- [ ] STRETCH — Build an offline replay/surrogate task to iterate faster while retaining live evaluation.
- [ ] STRETCH — Explore structured perception for player, obstacle, platform, and portal geometry.
- [ ] STRETCH — Compare recurrent policies with explicit frame stacking.
- [ ] STRETCH — Explore distributional or recurrent value-based algorithms for partial observability.
- [ ] STRETCH — Add curriculum learning across obstacle segments or levels.
- [ ] STRETCH — Add safe support for ship, ball, UFO, wave, robot, and spider action semantics.
- [ ] STRETCH — Evaluate multiple official levels and truly held-out levels.
- [ ] STRETCH — Investigate domain randomization for colors, cosmetics, resolution, and capture jitter.
- [ ] STRETCH — Investigate sample-efficient model-based or world-model approaches.
- [ ] STRETCH — Compare pixel policies with structured-feature policies under equal interaction budgets.
- [ ] STRETCH — Publish reusable environment components only after legal, packaging, and compatibility review.

---

## Checklist for every code change

- [ ] The issue states the problem and evidence.
- [ ] The learner writes what they expect to happen before running the change when it tests an RL concept.
- [ ] Acceptance criteria are testable.
- [ ] The change has the smallest reasonable scope.
- [ ] Public behavior/config/schema changes are versioned.
- [ ] Unit/regression tests cover the success and failure paths.
- [ ] Offline tests do not require Geometry Dash.
- [ ] Live verification is recorded when the change affects capture, input, timing, state, reset, or reward.
- [ ] Formatting, linting, typing, tests, and package build pass.
- [ ] Documentation and examples match the changed behavior.
- [ ] The learning log, ADR, or experiment report is updated when the change creates knowledge or a decision.
- [ ] The relevant learning module is updated in the learner's own words when the change applies a new RL concept.
- [ ] The milestone has an explicit media decision: captured, not visually useful, or capture failed.
- [ ] No game files, secrets, local paths, large artifacts, or personal desktop captures are staged.
- [ ] The commit message describes one coherent milestone.

## Checklist for every experiment

- [ ] Research question and falsifiable hypothesis are written before the run.
- [ ] The learner records a plain-language prediction before seeing the result.
- [ ] Parent/baseline experiment is identified.
- [ ] Primary metric, budget, seeds, and stop criteria are predeclared.
- [ ] Code commit is clean and recorded.
- [ ] Resolved config and contract versions are saved.
- [ ] Environment/hardware/dependency fingerprint is saved.
- [ ] Raw episode results and failure reasons are preserved.
- [ ] Checkpoints are integrity-checked and reload-tested.
- [ ] Evaluation is separated from training/model selection.
- [ ] Results include variability and all valid planned seeds.
- [ ] Plots/tables are generated from raw data.
- [ ] Representative success and failure media are linked.
- [ ] Any selected clip has shot ID, run/commit/checkpoint linkage, sidecar metadata, checksum, and backup status.
- [ ] Conclusion distinguishes evidence from inference.
- [ ] The reflection says what changed in the learner's understanding.
- [ ] Decision is recorded as adopt, reject, retry, or inconclusive.
- [ ] The next experiment changes one principal factor.

## Immediate next 12 work items

These are the critical path; finish them before adding an RL library.

1. [ ] DEFERRED — Return to L0 later: explain Geometry Dash as an MDP/POMDP and make a pre-experiment observation-stack prediction.
2. [ ] Checksum and back up the existing M05 state-flow video; capture M00 project origin and M01 human reference.
3. [x] Recreate the broken `.venv` from the Python 3.13/uv decision.
4. [x] Add `pyproject.toml`, dependency groups, `.python-version`, and `uv.lock`.
5. [x] Fix the `src` package/import boundaries and verify the built wheel in isolation.
6. [ ] Add formatting, linting, type checking, coverage, pre-commit, and Windows CI.
7. [ ] Finish the honest README/setup flow and choose the project license/governance basics.
8. [ ] Move Win32 control and screen detection out of `tools` into testable package modules.
9. [ ] Define the explicit screen-state machine, learn the episode/termination semantics, and collect a labeled multi-episode detector dataset.
10. [ ] Complete L1 return calculations, validate progress estimation, and choose reward contract v1.
11. [ ] Build versioned experiment configs, machine-readable results, checkpoint/resume, and media sidecar infrastructure.
12. [ ] Complete the bandit/tabular-Q learning modules and rerun stronger baselines before selecting DQN or PPO.

## First release handoff

- [ ] The clean-clone setup has been independently verified.
- [ ] CI and release build are green.
- [ ] The selected checkpoint and evaluation bundle are downloadable and checksum-verified.
- [ ] README claims match the final held-out results and exact supported scope.
- [ ] Architecture, environment contract, configs, protocol, results, model card, data card, safety/legal, troubleshooting, and roadmap are linked from the documentation index.
- [ ] The learning index contains completed own-word modules, runnable exercises, pre-run predictions, reflections, and assistance disclosures.
- [ ] Demo media is traceable, accessible, privacy-reviewed, and legally safe to publish.
- [ ] The montage has authentic baseline, failure/fix, learning, checkpoint-evolution, final-comparison, and limitation footage.
- [ ] License, citation, contributing, code of conduct, security policy, changelog, and release notes are present.
- [ ] The release is tagged and its reproduction procedure succeeds from downloaded artifacts.
