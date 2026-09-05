"""Offline golden-pixel and environment tests for observation contract v1."""

from __future__ import annotations

import unittest
from dataclasses import FrozenInstanceError
from typing import Any, cast
from unittest.mock import patch

import numpy as np
from PIL import Image

from geometry_dash_env import (
    OBSERVATION_CONTRACT_VERSION,
    OBSERVATION_LAYOUT,
    GeometryDashEnv,
)
from geometry_dash_env.observation import ObservationConfig, ObservationMode
from tests.test_environment import FakePlatform, FakeScreen


class ObservationTests(unittest.TestCase):
    def test_defaults_and_public_constants_are_frozen(self) -> None:
        config = ObservationConfig()
        self.assertEqual(OBSERVATION_CONTRACT_VERSION, "observation-rgb-hwc-v1")
        self.assertEqual(OBSERVATION_LAYOUT, "HWC")
        self.assertEqual(config.size, (160, 90))
        self.assertEqual(config.mode, "rgb")
        self.assertIsNone(config.crop)
        self.assertEqual(config.channels, 3)
        self.assertEqual(config.frame_shape, (90, 160, 3))
        self.assertEqual(config.shape(), config.frame_shape)
        with self.assertRaises(FrozenInstanceError):
            cast(Any, config).mode = "grayscale"

    def test_rgb_solid_image_has_exact_pixels_shape_and_dtype(self) -> None:
        pixels = ObservationConfig().transform(
            Image.new("RGBA", (320, 180), (12, 128, 255, 50))
        )
        self.assertEqual(pixels.shape, (90, 160, 3))
        self.assertEqual(pixels.dtype, np.uint8)
        for position in ((0, 0), (45, 80), (89, 159)):
            np.testing.assert_array_equal(pixels[position], [12, 128, 255])
        np.testing.assert_array_equal(
            pixels, np.full((90, 160, 3), [12, 128, 255], dtype=np.uint8)
        )

    def test_grayscale_has_singleton_channel_and_expected_luminance(self) -> None:
        config = ObservationConfig(size=(5, 3), mode="grayscale")
        pixels = config.transform(Image.new("RGB", (10, 6), (255, 0, 0)))
        self.assertEqual(config.channels, 1)
        self.assertEqual(pixels.shape, (3, 5, 1))
        self.assertEqual(pixels.dtype, np.uint8)
        np.testing.assert_array_equal(pixels, np.full((3, 5, 1), 76, dtype=np.uint8))

    def test_normalized_crop_selects_expected_color_on_both_axes(self) -> None:
        for axis in ("horizontal", "vertical"):
            with self.subTest(axis=axis):
                image = Image.new("RGB", (8, 6), (255, 0, 0))
                if axis == "horizontal":
                    image.paste((0, 0, 255), (4, 0, 8, 6))
                    crop = (0.5, 0.0, 1.0, 1.0)
                else:
                    image.paste((0, 0, 255), (0, 3, 8, 6))
                    crop = (0.0, 0.5, 1.0, 1.0)
                full = ObservationConfig(size=(8, 6)).transform(image)
                cropped = ObservationConfig(size=(8, 6), crop=crop).transform(image)
                np.testing.assert_array_equal(full[0, 0], [255, 0, 0])
                np.testing.assert_array_equal(
                    cropped, np.full((6, 8, 3), [0, 0, 255], dtype=np.uint8)
                )
                np.testing.assert_array_equal(
                    ObservationConfig(size=(8, 6), crop=(0, 0, 1, 1)).transform(image),
                    full,
                )

    def test_bilinear_golden_pixels_and_range(self) -> None:
        image = Image.new("RGB", (2, 1), (0, 0, 0))
        image.putpixel((1, 0), (255, 255, 255))
        for mode in ("rgb", "grayscale"):
            with self.subTest(mode=mode):
                config = ObservationConfig(
                    size=(3, 1), mode=cast(ObservationMode, mode)
                )
                pixels = config.transform(image)
                expected = np.repeat(
                    np.array([[[0], [128], [255]]], dtype=np.uint8),
                    config.channels,
                    axis=2,
                )
                np.testing.assert_array_equal(pixels, expected)
                self.assertEqual(pixels.dtype, np.uint8)
                self.assertEqual(int(pixels.min()), 0)
                self.assertEqual(int(pixels.max()), 255)

    def test_stack_shapes(self) -> None:
        for mode, channels in (("rgb", 3), ("grayscale", 1)):
            config = ObservationConfig(size=(7, 5), mode=cast(ObservationMode, mode))
            for stack in (1, 2, 4):
                with self.subTest(mode=mode, stack=stack):
                    frame_shape = (5, 7, channels)
                    expected = frame_shape if stack == 1 else (stack, *frame_shape)
                    self.assertEqual(config.shape(stack), expected)

    def test_invalid_sizes(self) -> None:
        for size in (
            (0, 90),
            (160, 0),
            (-1, 90),
            (160, -1),
            (1,),
            (1, 2, 3),
            (1.5, 90),
            (True, 90),
        ):
            with self.subTest(size=size), self.assertRaises(ValueError):
                ObservationConfig(size=cast(Any, size))

    def test_invalid_modes(self) -> None:
        for mode in ("RGB", "gray", "", None):
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                ObservationConfig(mode=cast(Any, mode))

    def test_invalid_crops(self) -> None:
        for crop in (
            (-0.1, 0, 1, 1),
            (0, -0.1, 1, 1),
            (0, 0, 1.1, 1),
            (0, 0, 1, 1.1),
            (0.5, 0, 0.5, 1),
            (0.8, 0, 0.2, 1),
            (0, 0.5, 1, 0.5),
            (0, 0.8, 1, 0.2),
            (0, 0, float("nan"), 1),
            (0, 0, 1, float("inf")),
            (0, 0, 1),
            (0, 0, 1, 1, 1),
        ):
            with self.subTest(crop=crop), self.assertRaises(ValueError):
                ObservationConfig(crop=cast(Any, crop))

    def test_invalid_stack_values(self) -> None:
        for stack in (0, -1, -4, 1.5, True, None):
            with self.subTest(stack=stack), self.assertRaises(ValueError):
                ObservationConfig().shape(cast(Any, stack))

    def test_transformed_arrays_do_not_alias_source_or_each_other(self) -> None:
        for mode in ("rgb", "grayscale"):
            with self.subTest(mode=mode):
                source = np.full((3, 5), 120, dtype=np.uint8)
                image = Image.fromarray(source)
                config = ObservationConfig(
                    size=(5, 3), mode=cast(ObservationMode, mode)
                )
                first = config.transform(image)
                second = config.transform(image)
                self.assertFalse(np.shares_memory(first, source))
                self.assertFalse(np.shares_memory(first, second))
                first.fill(0)
                self.assertEqual(image.getpixel((0, 0)), 120)
                image.putpixel((0, 0), 255)
                self.assertTrue(np.all(second == 120))
                self.assertTrue(np.all(first == 0))

    def test_environment_reset_records_geometry_config_and_actual_shape(self) -> None:
        image = Image.new("RGB", (800, 600), (255, 0, 0))
        image.paste((0, 0, 255), (400, 0, 800, 600))
        for mode, channels, color in (("rgb", 3, [0, 0, 255]), ("grayscale", 1, [29])):
            for stack in (1, 2, 4):
                with (
                    self.subTest(mode=mode, stack=stack),
                    GeometryDashEnv(
                        observation_size=(8, 6),
                        observation_mode=cast(ObservationMode, mode),
                        observation_crop=(0.5, 0, 1, 1),
                        frame_stack=stack,
                        reset_settle=0,
                        platform_backend=FakePlatform(),
                        capture_backend=FakeScreen(),
                    ) as env,
                ):
                    with (
                        patch("geometry_dash_env.environment.validate_game_path"),
                        patch.object(env, "_capture", return_value=image),
                        patch(
                            "geometry_dash_env.environment.classify_screen",
                            return_value="gameplay_or_transition",
                        ),
                        patch.object(
                            env, "_wait_for_ready_gameplay", return_value=image
                        ),
                    ):
                        observation, info = env.reset()
                    frame_shape = (6, 8, channels)
                    expected = frame_shape if stack == 1 else (stack, *frame_shape)
                    self.assertEqual(observation.shape, expected)
                    self.assertEqual(info["observation_shape"], expected)
                    self.assertEqual(env.observation_space.shape, expected)
                    self.assertTrue(env.observation_space.contains(observation))
                    np.testing.assert_array_equal(
                        observation, np.full(expected, color, dtype=np.uint8)
                    )
                    self.assertEqual(info["capture_bbox"], (0, 0, 800, 600))
                    self.assertEqual(info["observation_size"], (8, 6))
                    self.assertEqual(info["observation_mode"], mode)
                    self.assertEqual(info["observation_crop"], (0.5, 0, 1, 1))
                    self.assertEqual(info["frame_stack"], stack)
                    self.assertEqual(info["observation_layout"], "HWC")
                    self.assertEqual(
                        info["observation_contract_version"],
                        "observation-rgb-hwc-v1",
                    )


if __name__ == "__main__":
    unittest.main()
