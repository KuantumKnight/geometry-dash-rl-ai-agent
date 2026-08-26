"""Measure the current Geometry Dash environment loop without changing it."""

from __future__ import annotations

import argparse
import random
import time
from statistics import mean, median

from geometry_dash_env import GeometryDashEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a random-action benchmark against GeometryDashEnv."
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=100,
        help="Number of environment decisions to measure (default: 100).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for repeatable actions.",
    )
    args = parser.parse_args()
    if args.steps <= 0:
        parser.error("--steps must be positive")
    return args


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    env = GeometryDashEnv()
    timings_ms: list[float] = []
    deaths = 0
    resets = 0

    try:
        env.reset()
        resets += 1
        for index in range(args.steps):
            action = rng.choice([0, 1])
            started = time.perf_counter()
            _observation, reward, terminated, truncated, info = env.step(action)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            timings_ms.append(elapsed_ms)

            print(
                f"step={index + 1:03d} action={action} "
                f"elapsed_ms={elapsed_ms:8.2f} reward={reward:6.3f} "
                f"terminated={terminated} truncated={truncated} "
                f"frames={info['frames_elapsed']}"
            )

            if terminated:
                deaths += 1
            if terminated or truncated:
                env.reset()
                resets += 1

        total_seconds = sum(timings_ms) / 1000.0
        print()
        print(f"steps:             {len(timings_ms)}")
        print(f"mean step time:    {mean(timings_ms):.2f} ms")
        print(f"median step time:  {median(timings_ms):.2f} ms")
        print(f"min:               {min(timings_ms):.2f} ms")
        print(f"max:               {max(timings_ms):.2f} ms")
        print(f"decisions/sec:     {len(timings_ms) / total_seconds:.2f}")
        print(f"deaths:            {deaths}")
        print(f"resets:            {resets}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
