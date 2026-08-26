"""Run reproducible non-learning policies against the Geometry Dash environment."""

from __future__ import annotations

import argparse
import math
import random
import sys
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.geometry_dash_env import GeometryDashEnv  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--episodes",
        type=int,
        default=10,
        help="Episodes per policy (default: 10).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=300,
        help="Maximum decisions per episode (default: 300).",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=6,
        help="Periodic-jump interval in decisions (default: 6).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Base random seed (default: 42).",
    )
    args = parser.parse_args()
    if args.episodes <= 0 or args.max_steps <= 0 or args.period <= 0:
        parser.error("--episodes, --max-steps, and --period must be positive")
    return args


def choose_action(policy: str, step_index: int, rng: random.Random, period: int) -> int:
    if policy == "noop":
        return 0
    if policy == "random":
        return rng.choice([0, 1])
    if policy == "periodic":
        return int((step_index + 1) % period == 0)
    raise ValueError(f"Unknown policy: {policy}")


def run_policy(
    policy: str,
    *,
    episodes: int,
    max_steps: int,
    period: int,
    seed: int,
) -> dict[str, object]:
    env = GeometryDashEnv(max_steps=max_steps)
    rng = random.Random(seed)
    lengths: list[int] = []
    progresses: list[float] = []
    deaths = 0
    reset_failures = 0

    try:
        for episode_index in range(episodes):
            try:
                env.reset(seed=seed + episode_index)
            except Exception as exc:  # noqa: BLE001 - report unattended failures.
                reset_failures += 1
                print(
                    f"policy={policy} episode={episode_index + 1:03d} "
                    f"reset_failure={exc}"
                )
                break

            episode_length = 0
            terminal_progress: float | None = None
            while episode_length < max_steps:
                action = choose_action(policy, episode_length, rng, period)
                _observation, _reward, terminated, truncated, info = env.step(action)
                episode_length += 1
                if terminated:
                    deaths += 1
                    progress_ratio = info.get("progress_ratio")
                    if progress_ratio is not None:
                        terminal_progress = float(progress_ratio)
                    break
                if truncated:
                    break

            lengths.append(episode_length)
            if terminal_progress is not None:
                progresses.append(terminal_progress)
            progress_text = (
                f"{terminal_progress:.3f}" if terminal_progress is not None else "n/a"
            )
            print(
                f"policy={policy} episode={episode_index + 1:03d} "
                f"steps={episode_length:03d} progress={progress_text}"
            )
    finally:
        env.close()

    completed_episodes = len(lengths)
    average_progress = mean(progresses) if progresses else math.nan
    best_progress = max(progresses) if progresses else math.nan
    return {
        "policy": policy,
        "episodes": completed_episodes,
        "average_progress": average_progress,
        "best_progress": best_progress,
        "average_episode_length": mean(lengths) if lengths else math.nan,
        "death_rate": deaths / completed_episodes if completed_episodes else math.nan,
        "deaths": deaths,
        "progress_samples": len(progresses),
        "reset_failures": reset_failures,
    }


def format_metric(value: float, suffix: str = "") -> str:
    if math.isnan(value):
        return f"n/a{suffix}"
    if suffix == "%":
        return f"{value * 100:.1f}%"
    return f"{value:.3f}{suffix}"


def main() -> None:
    args = parse_args()
    policies = ("noop", "random", "periodic")
    results = []
    for policy_index, policy in enumerate(policies):
        results.append(
            run_policy(
                policy,
                episodes=args.episodes,
                max_steps=args.max_steps,
                period=args.period,
                seed=args.seed + policy_index * 100_000,
            )
        )

    print()
    print("baseline summary")
    print("policy    episodes  avg_progress  best_progress  avg_length  death_rate  resets_failed")
    for result in results:
        print(
            f"{result['policy']:<9} {result['episodes']:>8} "
            f"{format_metric(result['average_progress']):>13} "
            f"{format_metric(result['best_progress']):>14} "
            f"{format_metric(result['average_episode_length']):>11} "
            f"{format_metric(result['death_rate'], '%'):>11} "
            f"{result['reset_failures']:>13}"
        )
    print(f"periodic jump interval: {args.period} decisions")
    print(f"progress samples are terminal results-screen estimates")


if __name__ == "__main__":
    main()
