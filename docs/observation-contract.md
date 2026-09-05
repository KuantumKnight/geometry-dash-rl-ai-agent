# Observation contract v1

Version: `observation-rgb-hwc-v1`. Frame layout: `HWC` (channels last).

## Frozen default

`ObservationConfig` is the frozen, validated transform schema. The selected
v1 baseline is `size=(160, 90)` in **(width, height)** order, `mode="rgb"`,
`crop=None`, and environment `frame_stack=1`. This freezes an integration
baseline; comparative performance has not yet been established.

Sizes and stack depths must be positive integers. Modes are `rgb` and
`grayscale`. Invalid configuration raises `ValueError`.

## Transform and coordinates

The transform crops first, converts to RGB or Pillow luminance (`L`), then
resizes with bilinear resampling. A crop is `(left, top, right, bottom)` in
normalized coordinates relative to the original captured client image:

- The origin is the top-left; x increases rightward and y increases downward.
- Bounds must satisfy `0 <= left < right <= 1` and `0 <= top < bottom <= 1`.
- Horizontal coordinates multiply the original width; vertical coordinates
  multiply the original height. Pillow rounds the resulting crop box to pixel
  boundaries; right and bottom are exclusive.
- `None` retains the full capture; `(0, 0, 1, 1)` selects the full image.
- `(0.5, 0, 1, 1)` selects the right half before resizing.

Reset info records the original `capture_bbox` in desktop pixels as
`(left, top, right, bottom)`; capture dimensions are `(right-left, bottom-top)`.
It also records `observation_contract_version`, `observation_layout`,
`observation_size`, `observation_mode`, `observation_crop`, `observation_shape`,
and `frame_stack`. These describe the actual configured transform and tensor.

## Tensor boundary

Every result is an independent, writable NumPy `uint8` array with values in
`[0, 255]`. There is no floating-point normalization or channel transposition.

| Configuration | Shape | Default RGB example |
| --- | --- | --- |
| One frame | `(H, W, C)` | `(90, 160, 3)` |
| N stacked frames, N > 1 | `(N, H, W, C)` | `(4, 90, 160, 3)` |

`N` is temporal depth, not a batch axis. Stacks run oldest to newest; reset
fills all slots with copies of the initial frame. `OBSERVATION_LAYOUT="HWC"`
describes each frame even when a stack axis is present. The environment's
observation space and returned arrays use these exact shapes.

Grayscale is an explicit candidate selected with `observation_mode="grayscale"`.
It retains `C=1`, giving `(90, 160, 1)` or `(N, 90, 160, 1)` at the default
size. Crops, alternate sizes, and stacks are also explicit candidate settings;
persist their configuration alongside the version to distinguish experiments.

## Offline validation and open evidence

Validate the versioned schema, synthetic golden pixels, bilinear interpolation,
crop axes, shapes, dtype/range, array independence, and reset metadata with:

```powershell
uv run python -m unittest tests.test_observation -v
```

The fake-backend environment tests cover RGB and grayscale with stack depths
1, 2, and 4. Training-library selection and its adapter/integration checks
remain open; any required normalization or layout conversion must be explicit.

Live transform latency (including p95/p99), the decision-budget smoke test,
and fixed-dataset comparisons of color mode, crop, resolution, and temporal
depth remain open. These offline tests do not establish a fastest or best
representation. This document specifies the observation contract; a joint
observation/action acceptance ADR remains open.
