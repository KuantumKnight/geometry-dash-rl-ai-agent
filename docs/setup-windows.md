# Windows Setup

This is the clean-clone setup path for the supported platform.

## Prerequisites

- Windows 10 or later with a visible desktop session.
- A legitimate local Geometry Dash installation.
- Python 3.12 or 3.13.
- uv available on PATH.
- Optional ffmpeg for MP4 recording.

The repository does not distribute the game executable or extracted game
assets.

## Install

    git clone https://github.com/KuantumKnight/geometry-dash-rl-ai-agent.git
    cd geometry-dash-rl-ai-agent
    uv sync --dev
    uv run python -m unittest discover -s tests -v

The offline test command must pass before any live command is attempted.

## Configure the executable

The default path is Geometry Dash\GeometryDash.exe beneath the repository
root. For another installation, set the process-local override:

    $env:GEOMETRY_DASH_EXE = 'D:\Games\Geometry Dash\GeometryDash.exe'

The configured path must exist and end in .exe. Do not add the game folder,
recordings, checkpoints, or generated artifacts to git.

## Live preflight

Start the game manually at the target level in cube mode. Keep the client
visible, focused, and at a fixed position and size. Confirm that no sensitive
desktop application is behind the game, then inspect help before sending input:

    uv run python tools\capture_action.py --help
    .\scripts\dev.ps1 -Task test-live -ConfirmLive

The emergency stop is the host binding Ctrl+Shift+F12. Live qualification
results must include the exact game version/settings and a redacted system
configuration; those values cannot be inferred from the executable.

## Current limits

The environment supports only Windows, Stereo Madness, cube mode, two actions,
heuristic screen detection, and a provisional terminal reward. Training,
evaluation, checkpointing, and resume are not implemented.
