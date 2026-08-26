"""Check that repeated captures keep a stable, current client bounding box."""

from __future__ import annotations

import argparse

from geometry_dash_env import GeometryDashEnv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="Number of consecutive captures to check (default: 100).",
    )
    args = parser.parse_args()
    if args.samples <= 0:
        parser.error("--samples must be positive")
    return args


def main() -> None:
    args = parse_args()
    env = GeometryDashEnv()
    boxes: list[tuple[int, int, int, int]] = []
    sizes: list[tuple[int, int]] = []

    try:
        env.reset()
        for _ in range(args.samples):
            image = env._capture()
            if env._bbox is None:
                raise RuntimeError("Capture completed without a tracked bounding box")
            boxes.append(env._bbox)
            sizes.append(image.size)

        print(f"samples:             {len(sizes)}")
        print(f"unique bounding boxes: {len(set(boxes))}")
        print(f"unique image sizes:   {len(set(sizes))}")
        print(f"first bbox:           {boxes[0]}")
        print(f"last bbox:            {boxes[-1]}")
        print(f"first image size:     {sizes[0]}")
        print(f"last image size:      {sizes[-1]}")
    finally:
        env.close()


if __name__ == "__main__":
    main()
