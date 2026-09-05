"""Validate a baseline config without starting Geometry Dash."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from pathlib import Path

from geometry_dash_env.experiment import RunManager, load_config, resolve_config
from geometry_dash_env.metrics import summarize_episodes


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
    parser.add_argument(
        "--unattended-dry-run",
        action="store_true",
        help="write a deterministic offline run without live interaction",
    )
    parser.add_argument("--episodes", type=int, default=100)
    parser.add_argument("--steps", type=int, default=100)
    return parser.parse_args()


def main() -> None:
    """Validate config or exercise the artifact pipeline without live input."""

    args = parse_args()
    config = load_config(args.config)
    if args.unattended_dry_run:
        if args.episodes <= 0 or args.steps <= 0:
            raise SystemExit("episodes and steps must be positive")
        run_config = resolve_config({**config, "system": {"exploratory": True}})
        manager = RunManager.create(
            args.output,
            run_config,
            command="tools/run_baseline.py --unattended-dry-run",
            seed=args.seed,
        )
        manager.set_state("running")
        rows: list[Mapping[str, object]] = []
        with manager.interruption_guard(lambda: {"step": 0, "episode": 0}):
            for episode in range(args.episodes):
                for step in range(args.steps):
                    manager.record_step(
                        {
                            "episode": episode,
                            "step": step,
                            "requested_action": 0,
                            "detector_confidence": None,
                            "detector_errors": [],
                            "missed_deadline": False,
                        }
                    )
                row = {
                    "episode": episode,
                    "return": 0.0,
                    "length": args.steps,
                    "progress": 0.0,
                    "outcome": "truncation",
                    "reset_failures": 0,
                }
                rows.append(row)
                manager.record_episode(row)
            manager.write_summary(summarize_episodes(rows, seed=args.seed))
            manager.save_checkpoint("final", {"step": args.episodes * args.steps})
            manager.set_state("completed", reason="budget")
        print(f"run_id={manager.run_id}")
        print(f"run_dir={manager.run_dir}")
        return
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
