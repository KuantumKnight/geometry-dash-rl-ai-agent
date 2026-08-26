# Experiment environment fingerprint

This file records the host used for the current live prototype evidence. It is a provenance record, not a claim that these settings generalize to other machines.

## Snapshot

Captured on 2026-08-26 from the Windows host running the local Geometry Dash process and repository.

| Field | Recorded value | Source/notes |
| --- | --- | --- |
| Operating system | Windows 11 Home Single Language, version `10.0.26200`, build `26200`, 64-bit | `Win32_OperatingSystem` |
| Computer | Alienware 16X Aurora `AC16251` | `Win32_ComputerSystem` |
| CPU | Intel Core Ultra 9 275HX, 24 cores / 24 logical processors | `Win32_Processor` |
| Installed RAM | 16,597,598,208 bytes (approximately 15.46 GiB) | `Win32_ComputerSystem` |
| GPU 1 | Intel Graphics, driver `32.0.101.8724` | `Win32_VideoController` |
| GPU 2 | NVIDIA GeForce RTX 5070 Laptop GPU, driver `32.0.16.1062` | `Win32_VideoController` |
| Active display | One active `LGD07A3` monitor | `WmiMonitorBasicDisplayParams` |
| Display mode | `2560×1600` at `240 Hz` | `Win32_VideoController` |
| Windows scaling | 150% (`144` logical DPI) | `Win32_DesktopMonitor`; 96 DPI base |
| Geometry Dash executable | Local `Geometry Dash/GeometryDash.exe`, 10,700,288 bytes, modified 2026-01-22 18:30:49 | File metadata; version-resource fields are empty |
| Live client capture | `800×600` pixels in the current visible window | `game_client_bbox()` and focused screenshot |
| Project Python | CPython `3.13.14` from the locked `.venv` | `uv run python --version` |

## Provenance limits

The historical logs identify the same project and date but do not embed a machine fingerprint. This snapshot is therefore the best available record and should be treated as “current host, historical equivalence not independently proven” until the original run is confirmed by the author.

Game version, window mode, VSync/FPS setting, level speed, and other in-game settings remain open roadmap checks because they cannot be recovered exactly from the executable metadata or the current capture alone.

## Geometry Dash version evidence gap

The local executable has empty `ProductVersion`, `FileVersion`, `ProductName`, and `CompanyName` version-resource fields. No Steam app manifest was present in the checked standard Steam locations. The current process is confirmed as `Geometry Dash.exe`, but these facts do not identify its game release.

The exact version must be recorded from the in-game UI or the store page in a future evidence capture. This roadmap check intentionally remains open.

## In-game configuration evidence gap

A focused live capture on 2026-08-26 visibly showed the `Stereo Madness` results overlay (`Attempt 305`, `1%`) in an `800×600` client capture. That confirms the target level and current capture geometry, but it does not prove the settings required by the roadmap check:

| Setting | Current evidence | Status |
| --- | --- | --- |
| Window mode | Visible window; exact windowed/borderless/fullscreen mode not recorded | Open |
| Client resolution | `800×600` capture | Recorded |
| VSync / game FPS setting | Not visible in the capture or executable metadata | Open |
| Level | `Stereo Madness` visible in the results overlay | Recorded |
| Character/mode | Project scope says cube, but this capture does not prove the in-game mode | Open |
| Game speed | Not visible in the capture | Open |

The environment's own `fps=60` and `frame_skip=4` are Python controller settings, not evidence of the game's VSync or speed settings. The roadmap check remains open until the in-game settings are captured directly.

## Video capture provenance

The host provides `ffmpeg version 8.1.1-full_build-www.gyan.dev` (build dated 2026). The preserved candidate `artifacts/episodes/20260826T113120Z/episode.mp4` is an H.264 MP4 at `800×600`, 60 FPS, 20 seconds, and 1,200 frames. Video encoding was enabled for this episode recorder run; the benchmark tools themselves do not encode video.
