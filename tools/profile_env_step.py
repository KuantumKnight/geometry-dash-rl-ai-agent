"""Profile the existing per-frame environment components without changing them."""

from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path
from statistics import mean

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.geometry_dash_env import GeometryDashEnv  # noqa: E402
from tools.capture_action import send_jump  # noqa: E402
from tools.game_state import is_death_screen  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Profile sleep, capture, detection, and observation conversion."
    )
    parser.add_argument(
        "--frames",
        type=int,
        default=100,
        help="Number of frames to profile (default: 100).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for repeatable actions.",
    )
    args = parser.parse_args()
    if args.frames <= 0:
        parser.error("--frames must be positive")
    return args


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)
    env = GeometryDashEnv()
    measurements: list[dict[str, float]] = []
    deaths = 0
    resets = 0

    try:
        env.reset()
        resets += 1
        for index in range(args.frames):
            action = rng.choice([0, 1])
            if action == 1:
                send_jump(env._hwnd)

            frame_started = time.perf_counter()

            sleep_started = time.perf_counter()
            time.sleep(1.0 / env.fps)
            sleep_ms = (time.perf_counter() - sleep_started) * 1000.0

            capture_started = time.perf_counter()
            image = env._capture()
            capture_ms = (time.perf_counter() - capture_started) * 1000.0

            detection_started = time.perf_counter()
            dead = is_death_screen(image)
            detection_ms = (time.perf_counter() - detection_started) * 1000.0

            observation_started = time.perf_counter()
            env._observation(image)
            observation_ms = (time.perf_counter() - observation_started) * 1000.0

            total_ms = (time.perf_counter() - frame_started) * 1000.0
            measurements.append(
                {
                    "sleep": sleep_ms,
                    "capture": capture_ms,
                    "death": detection_ms,
                    "observation": observation_ms,
                    "total": total_ms,
                }
            )
            print(
                f"frame={index + 1:03d} action={action} "
                f"sleep_ms={sleep_ms:7.2f} capture_ms={capture_ms:7.2f} "
                f"death_ms={detection_ms:7.2f} observation_ms={observation_ms:7.2f} "
                f"total_ms={total_ms:7.2f} dead={dead}"
            )

            if dead:
                deaths += 1
                env.reset()
                resets += 1

        averages = {
            name: mean(item[name] for item in measurements)
            for name in ("sleep", "capture", "death", "observation", "total")
        }
        measured_components = sum(
            averages[name] for name in ("sleep", "capture", "death", "observation")
        )

        print()
        print(f"frames:             {len(measurements)}")
        print(f"mean sleep:         {averages['sleep']:.2f} ms")
        print(f"mean capture:       {averages['capture']:.2f} ms")
        print(f"mean death detect:  {averages['death']:.2f} ms")
        print(f"mean observation:   {averages['observation']:.2f} ms")
        print(f"mean frame total:   {averages['total']:.2f} ms")
        print(f"unaccounted:        {averages['total'] - measured_components:.2f} ms")
        print(f"deaths:             {deaths}")
        print(f"resets:             {resets}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
