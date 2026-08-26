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
