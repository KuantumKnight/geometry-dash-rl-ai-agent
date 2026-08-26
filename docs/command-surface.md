# Current command surface

All commands run through the locked project environment with `uv run`. The repository intentionally exposes only operations that currently have an implementation.

## Available commands

| Operation | Command | Game required |
| --- | --- | --- |
| Capture/no-op or jump | `uv run python tools\\capture_action.py --help` | Live command: yes |
| Environment benchmark | `uv run python tools\\benchmark_env.py --help` | Live command: yes |
| Non-learning baseline | `uv run python tools\\baseline_agent.py --help` | Live command: yes |
| Record frames/video | `uv run python tools\\record_frames.py --help` | Live command: yes |
| Offline detector benchmark | `uv run python tools\\benchmark_detector_offline.py --help` | No; saved PNGs only |
| Episode scan | `uv run python tools\\scan_episode.py --help` | No; saved frames only |
| Reset stress test | `uv run python tools\\stress_reset.py --help` | Live command: yes |
| Capture stability | `uv run python tools\\verify_capture_stability.py --help` | Live command: yes |

Every listed CLI has a parser-level `--help` path and fails before sending input when the required game executable/window is unavailable. Live commands must only be run when Geometry Dash is visible and desktop focus is safe.

## Intentionally absent commands

There is no `train` or `evaluate` command yet. A learning algorithm, checkpoint format, reward protocol, and held-out evaluation protocol have not been selected, so adding placeholder entry points would make the public interface look more complete than the project is. The roadmap item for the full six-operation entrypoint set remains open until those operations are real.
