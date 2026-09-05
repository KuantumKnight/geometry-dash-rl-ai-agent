"""Validate a baseline config without starting Geometry Dash."""

from __future__ import annotations

import argparse
from pathlib import Path

from geometry_dash_env.experiment import load_config


def parse_args() -> argparse.Namespace:
    """Parse baseline config validation arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("configs/baseline.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/runs"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate config without live interaction",
    )
    return parser.parse_args()


def main() -> None:
    """Load the committed config and print its identity."""

    args = parse_args()
    config = load_config(args.config)
    if not args.dry_run:
        raise SystemExit(
            "live baseline execution is gated until the reference setup is qualified; "
            "use --dry-run"
        )
    print(f"config={args.config}")
    print(f"output={args.output}")
    print(f"seed={args.seed}")
    print(f"sections={len(config)}")
    print("baseline configuration is valid")


if __name__ == "__main__":
    main()
