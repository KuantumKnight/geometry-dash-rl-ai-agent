"""Run unattended no-op episodes and count reset failures."""

from __future__ import annotations

import argparse

from geometry_dash_env import GeometryDashEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--deaths",
        type=int,
        default=50,
        help="Number of detected deaths to reach (default: 50).",
    )
    parser.add_argument(
        "--max-episode-steps",
        type=int,
        default=300,
        help="Maximum no-op decisions allowed per episode (default: 300).",
    )
    args = parser.parse_args()
    if args.deaths <= 0 or args.max_episode_steps <= 0:
        parser.error("--deaths and --max-episode-steps must be positive")
    return args


def main() -> None:
    args = parse_args()
    env = GeometryDashEnv(max_steps=args.max_episode_steps)
    deaths = 0
    reset_attempts = 0
    reset_failures = 0
    episode_failures = 0

    try:
        while deaths < args.deaths:
            reset_attempts += 1
            try:
                env.reset()
            except Exception as exc:
                reset_failures += 1
                print(f"reset_failure={reset_failures} error={exc}")
                break

            episode_ended = False
            for step in range(args.max_episode_steps):
                _observation, _reward, terminated, truncated, _info = env.step(0)
                if terminated:
                    deaths += 1
                    episode_ended = True
                    print(
                        f"death={deaths:03d} reset_attempt={reset_attempts:03d} "
                        f"steps={step + 1}"
                    )
                    break
                if truncated:
                    episode_failures += 1
                    print(
                        f"episode_failure={episode_failures} "
                        f"reason=truncated reset_attempt={reset_attempts:03d}"
                    )
                    break

            if not episode_ended and deaths < args.deaths:
                episode_failures += 1
                print(
                    f"episode_failure={episode_failures} "
                    f"reason=no_death reset_attempt={reset_attempts:03d}"
                )
                break

        print()
        print(f"target deaths:     {args.deaths}")
        print(f"deaths reached:    {deaths}")
        print(f"reset attempts:    {reset_attempts}")
        print(f"reset failures:    {reset_failures}")
        print(f"episode failures:  {episode_failures}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
