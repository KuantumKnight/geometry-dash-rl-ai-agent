# Progress Contract v1

The first progress contract uses the normalized normal-mode results-screen
bar fill as the authoritative terminal progress measurement. It is bounded
to [0, 1], where 0 means no visible fill and 1 means a full bar. Unreadable,
out-of-range, non-finite, and non-gameplay measurements are missing data; they
are never converted to fabricated zero progress.

ProgressTracker is the versioned offline primitive for a future continuous
signal. It emits raw and filtered values, newly achieved progress_delta,
missing-data status, forward-jump clamping, and backward-motion anomalies.
The first sample establishes an episode baseline and contributes no delta.
Repeated values and small jitter contribute no delta. A reset clears the
episode baseline.

The default jitter tolerance is 0.005 normalized progress and the default
maximum forward delta per update is 0.10. These are configuration values, not
detector accuracy claims; they require held-out/live calibration before being
used for training reward.
