"""Versioned channels-last pixel observation configuration and transforms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from PIL import Image

OBSERVATION_CONTRACT_VERSION = "observation-rgb-hwc-v1"
OBSERVATION_LAYOUT = "HWC"
ObservationMode = Literal["rgb", "grayscale"]


@dataclass(frozen=True)
class ObservationConfig:
    """Immutable transform schema with size expressed as (width, height)."""

    size: tuple[int, int] = (160, 90)
    mode: ObservationMode = "rgb"
    crop: tuple[float, float, float, float] | None = None

    def __post_init__(self) -> None:
        if len(self.size) != 2 or any(
            not isinstance(dimension, int)
            or isinstance(dimension, bool)
            or dimension <= 0
            for dimension in self.size
        ):
            raise ValueError("size must contain two positive integer dimensions")
        if self.mode not in ("rgb", "grayscale"):
            raise ValueError("mode must be 'rgb' or 'grayscale'")
        if self.crop is not None:
            if len(self.crop) != 4:
                raise ValueError("crop must contain left, top, right, bottom")
            left, top, right, bottom = self.crop
            if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
                raise ValueError(
                    "crop must satisfy 0 <= left < right <= 1 and "
                    "0 <= top < bottom <= 1"
                )

    @property
    def channels(self) -> int:
        """Return the number of channels in each transformed frame."""
        return 3 if self.mode == "rgb" else 1

    @property
    def frame_shape(self) -> tuple[int, int, int]:
        """Return the channels-last (height, width, channels) frame shape."""
        return (self.size[1], self.size[0], self.channels)

    def shape(self, frame_stack: int = 1) -> tuple[int, ...]:
        """Return the observation shape, with a leading axis for stacked frames."""
        if (
            not isinstance(frame_stack, int)
            or isinstance(frame_stack, bool)
            or frame_stack <= 0
        ):
            raise ValueError("frame_stack must be a positive integer")
        if frame_stack == 1:
            return self.frame_shape
        return (frame_stack, *self.frame_shape)

    def transform(self, image: Image.Image) -> np.ndarray:
        """Crop, convert, and bilinearly resize into independent uint8 pixels."""
        if self.crop is not None:
            left, top, right, bottom = self.crop
            width, height = image.size
            image = image.crop(
                (left * width, top * height, right * width, bottom * height)
            )
        image = image.convert("RGB" if self.mode == "rgb" else "L")
        image = image.resize(self.size, Image.Resampling.BILINEAR)
        pixels = np.asarray(image, dtype=np.uint8)
        if self.mode == "grayscale":
            pixels = pixels[..., np.newaxis]
        return pixels.copy()
