# Geometry Dash Screen-State Map

Source episode: `artifacts/episodes/20260826T113120Z`
Capture rate: 60 FPS video with 5 FPS PNG samples
Level shown: Stereo Madness

The frame ranges below use the sampled PNG indices. Each sampled frame is approximately 0.2 seconds apart, so the boundaries are approximate.

| State | Sampled frames | What it contains | RL meaning |
| --- | ---: | --- | --- |
| `MAIN_MENU` | 0–10 | Geometry Dash home screen and main navigation buttons | Outside the episode; do not train on these frames |
| `LEVEL_INFO` | 11–18 | Stereo Madness level card, progress, normal/practice mode controls | Setup UI; wait for level start |
| `ATTEMPT_INTRO` | 19–23 | Fade transition and `ATTEMPT 1` overlay | Episode has begun, but gameplay pixels are not yet stable |
| `GAMEPLAY` | 24–45 | Player, hazards, platforms, and scrolling level | Valid observation/action loop |
| `DEATH_ANIMATION` | 46–48 | Player collision, explosion, and fade into the result screen | Terminal transition; stop issuing normal actions |
| `RESULTS` | 49–77 | Attempt summary with progress, jumps, time, retry, and menu buttons | Terminal state; candidate point for reset |
| `ATTEMPT_INTRO` | 78–82 | `ATTEMPT 2` transition back into the level | Reset succeeded; wait for gameplay |
| `GAMEPLAY` | 83–99 | Second gameplay segment | Valid observation/action loop |

## Environment implications

The first environment should expose only `GAMEPLAY` frames to the policy. UI and transition states should be handled by the environment controller:

```text
MAIN_MENU → LEVEL_INFO → ATTEMPT_INTRO → GAMEPLAY
                                               ↓
                                  DEATH_ANIMATION → RESULTS
                                                           ↓
                                                    ATTEMPT_INTRO
```

The existing death detector covers the `RESULTS` appearance on the recorded episode. The next implementation should add explicit handling for `ATTEMPT_INTRO` and `GAMEPLAY`, then test the `RESULTS → retry → ATTEMPT_INTRO → GAMEPLAY` reset path.

## Important limitation

This map is evidence from one recorded run, not a universal classifier. Screen colors, animation timing, and level layouts can vary. Keep collecting traces as the detector evolves.
