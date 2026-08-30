# Contributing

This project is an educational Windows reinforcement-learning experiment. Keep
changes small, evidence-driven, and within the documented Geometry Dash scope.

## Before opening a pull request

1. Read the relevant section of docs/roadmap.md.
2. State the problem, evidence, acceptance criteria, and expected result.
3. Keep proprietary game files, recordings, checkpoints, secrets, and local
   paths out of git.
4. Add offline tests for success and failure paths. Live-only checks must be
   recorded as live evidence and must never be required by default CI.
5. Update the API, command, roadmap, learning, or experiment documentation
   when behavior or evidence changes.

## Local verification

    uv sync --dev
    uv run ruff format --check src tests tools
    uv run ruff check src tests tools
    uv run pyright
    uv run coverage run -m unittest discover -s tests -v
    uv run coverage report
    uv run python -m build

Use the live commands only after reviewing the safety instructions and
confirming that desktop focus is safe.

## Pull requests

One pull request should represent one coherent milestone. Include the exact
verification commands and results, identify any live checks not run, and link
the roadmap items completed by the change. Do not mark a checkbox complete from
code existence alone; record the acceptance evidence first.
