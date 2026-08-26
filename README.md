# Learning Reinforcement Learning by Teaching an Agent to Play Geometry Dash

A Windows-based reinforcement-learning project built from the game-control loop upward: capture pixels, choose an action, measure progress, reset reliably, train an agent, and test whether it actually beats simple baselines.

This repository has three equal goals:

1. build a trustworthy Geometry Dash RL agent;
2. prove the creator learned the RL ideas through predictions, exercises, experiments, and explanations;
3. preserve authentic footage of failures and breakthroughs for a future technical montage.

> **Current truth:** the environment and first non-learning baselines exist. No trained learning agent or released checkpoint exists yet.

## Project status

| Area | Status | Evidence |
| --- | --- | --- |
| Pixel capture and game actions | Prototype complete | Source, tools, and chronological [learning log](docs/learning-log.md) |
| Gymnasium-style environment | Prototype complete | `reset()`, `step()`, spaces, timing, termination, and frame stacking |
| Offline unit tests | 10 passing in the locked Python 3.13 environment | `uv run python -m unittest discover -s tests -v` |
| Live reset reliability | Historical qualification | 50 recorded consecutive deaths/resets with zero recorded failures |
| Live decision speed | Historical qualification | 83.42 ms mean step time / 11.99 decisions per second over 100 steps |
| Non-learning baseline | Initial measurement complete | Random policy: 4.8% best and 1.9% average terminal progress over 10 episodes |
| RL theory curriculum | Planned, not yet completed | [RL learning journey](docs/learning/README.md) |
| Learning agent | Not implemented | Algorithm selection intentionally follows environment/reward/evaluation gates |
| Montage archive | One candidate plus planned shot list | [Media log](docs/media-log.md) and [montage plan](docs/montage-plan.md) |
| Reproducible local environment/package | Complete locally; CI workflow added, public run pending | `pyproject.toml`, `.python-version`, and `uv.lock` |
| Offline quality gates | Complete locally; Windows matrix workflow added | Ruff, Pyright, coverage, pre-commit, and `.github/workflows/quality.yml` |

Historical live results were recorded on one machine and were not rerun during the documentation audit. They are engineering evidence, not general performance claims.

## System loop

```text
Geometry Dash window
        ↓ pixels
screen capture → state/observation → policy → no-op or jump
        ↑                                      ↓
 reset/controller ← terminal + progress ← next game frame
```

The current scope is deliberately narrow: Windows, Stereo Madness, cube mode, and two actions. The environment uses pixel observations and heuristic screen/progress detection while the project builds toward a validated training protocol.

## Learning in public

The [RL learning journey](docs/learning/README.md) is the proof-of-understanding track. Each completed concept must include:

- an explanation in the learner's own words;
- a falsifiable prediction written before the run;
- a hand calculation or small from-scratch implementation;
- tests and measured results;
- a reflection on what changed in the learner's understanding;
- a direct connection to the Geometry Dash agent;
- disclosure of tutorials, libraries, people, and AI assistance.

The curriculum moves just in time from MDP/POMDP framing and returns through Bellman reasoning, exploration, tabular Q-learning, pixel/CNN representations, DQN, PPO trade-offs, training discipline, and multi-seed evaluation. Empty notes or copied definitions do not count as completed learning.

## Video evidence and future montage

The [montage capture plan](docs/montage-plan.md) defines 23 story shots covering the original baseline, environment perception/control, detector failures, reward visualization, toy RL learning, first live improvement, checkpoint evolution, final held-out comparison, and honest limitations.

The [media evidence log](docs/media-log.md) records footage that actually exists. Selected clips must link to their commit, run/config, checkpoint, learning note, checksum, and backup. Raw footage stays out of normal git history.

The existing 20-second state-flow candidate already shows:

```text
main menu → level info → attempt intro → gameplay → death/results → retry → gameplay
```

It still needs a checksum, second backup, and privacy/rights review before it is considered preserved.

## Repository map

```text
src/geometry_dash_env/   Environment implementation
tests/                   Offline contract tests
tools/                   Capture, reset, benchmark, baseline, and recording prototypes
docs/learning/           RL curriculum and future proof-of-learning notes/exercises
docs/decisions/          Architecture decision records
docs/learning-log.md     Chronological engineering history
docs/media-log.md        Catalog of footage that actually exists
docs/montage-plan.md     Planned montage story and capture standard
docs/roadmap.md          Master engineering, learning, documentation, and release checklist
artifacts/               Local generated frames, videos, telemetry, and results; gitignored
Geometry Dash/           Local proprietary game installation; gitignored
```

## Set up the development environment

The project uses [uv](https://docs.astral.sh/uv/) with Python 3.13. Runtime and development dependencies are locked in `uv.lock`.

For a single PowerShell command surface, use `.\scripts\dev.ps1 -Task help`. It exposes setup, quality, offline-test, live-smoke, and benchmark tasks; live tasks require `-ConfirmLive`, while future `train` and `evaluate` tasks fail closed until implemented.

```powershell
git clone https://github.com/KuantumKnight/geometry-dash-rl-ai-agent.git
cd geometry-dash-rl-ai-agent
uv sync --dev
uv run python -m unittest discover -s tests -v
```

Expected offline result: 10 passing tests. The repository's quality gate is reproducible locally:

```powershell
uv run ruff format --check src tests tools
uv run ruff check src tests tools
uv run pyright
uv run coverage run -m unittest discover -s tests -v
uv run coverage report
uv run pre-commit run --all-files
uv run python -m build
```

Coverage currently enforces a 60% branch-aware floor on testable package logic; the Win32 input module is intentionally excluded because it requires a live Windows desktop. A Windows GitHub Actions matrix repeats the offline gate on Python 3.12 and 3.13 without downloading or launching Geometry Dash.

The default live-game path is `Geometry Dash/GeometryDash.exe` under the repository root. Keep the proprietary game directory local and gitignored. To use another location for the executable:

```powershell
$env:GEOMETRY_DASH_EXE = 'D:\Games\Geometry Dash\GeometryDash.exe'
```

Inspect a live tool without sending input:

```powershell
uv run python tools\capture_action.py --help
uv run python tools\baseline_agent.py --help
```

Live tools expect Windows, a legitimate Geometry Dash installation, the game running in a visible window, and optional `ffmpeg` for MP4 creation. The training dependency group and learning agent are intentionally not added yet.

## Safety and legal scope

Live tools can focus the Geometry Dash window and send keyboard/mouse input. Do not run them while using other sensitive desktop applications, and stop immediately if focus or state detection is wrong.

The game executable, extracted game assets, checkpoints, raw recordings, and generated artifacts are not committed to the repository. Users must supply their own legitimate game installation. This is an independent educational project and is not affiliated with or endorsed by RobTop Games.

## Documentation

- [Master build checklist](docs/roadmap.md)
- [RL learning journey](docs/learning/README.md)
- [Learning/engineering log](docs/learning-log.md)
- [Environment API](docs/environment-api.md)
- [Command surface](docs/command-surface.md)
- [Developer commands](docs/developer-commands.md)
- [Screen-state map](docs/screen-state-map.md)
- [Montage capture plan](docs/montage-plan.md)
- [Media evidence log](docs/media-log.md)
- [Architecture decisions](docs/decisions/0001-rl-environment-interface.md)
- [Packaging decision](docs/decisions/0002-python-packaging-and-locking.md)
- [Quality gates decision](docs/decisions/0003-quality-gates-and-ci.md)

## License

No license has been selected yet. Until a license is added, do not assume permission to copy, modify, or redistribute the source.
