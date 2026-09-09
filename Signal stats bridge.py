"""
signal_stats_bridge.py
================
The ONLY path by which EEG or hormone telemetry may reach
research_art_generator.py / research_video_generator.py — and it only
ever passes through as abstract numeric statistics (variance, mean),
never raw readings, never anything claimed to represent brain
activity or endocrine state.

READ THIS BEFORE MODIFYING THIS FILE
-----------------------------------------
This file exists because of an explicit boundary set earlier in this
project: AI-generated images/video have no actual scientific
relationship to a person's EEG or hormone readings, no matter how
they're prompted, and presenting one as if it depicted a person's
brain or body would be misleading regardless of consent or an opt-in
flag. What consent DOES legitimately unlock is treating these signals
as more abstract data channels — same status as a MOS score — for
generating abstract art/video. It does NOT unlock generating imagery
that claims biological meaning. If you're tempted to add anatomical
language to a prompt here, or to make output claim to "show" someone's
brain/hormone state: don't — that's the exact line this file exists
to hold.

WHAT THIS ACTUALLY COMPUTES
--------------------------------
Given a list of consented readings (already gone through
digital_dna.py's add_live_signal() consent gate, source=
"eeg_telemetry" or "hormone_telemetry"), this computes real,
ordinary statistics — count, mean, variance — nothing more. No
frequency-band analysis claiming to detect "focus" or "stress," no
hormone-level interpretation claiming physiological meaning. Just
numbers, the same category of thing a MOS score already is.

Usage
-----
    from signal_stats_bridge import signal_channel_stats

    stats = signal_channel_stats(eeg_readings, label="eeg")
    # -> {"eeg_count": 40, "eeg_mean": 12.3, "eeg_variance": 0.4}

    # then pass into the art/video generators as extra_signal_stats:
    result = generate_network_art(mos_score, topic_count,
                                    extra_signal_stats=stats)
"""

from __future__ import annotations
import statistics


def signal_channel_stats(readings: list[float], label: str) -> dict:
    """Real, boring statistics — nothing that implies biological meaning.
    `readings` should already be whatever numeric values your consented
    capture pipeline produced (e.g. a band-power number, a hormone
    concentration) — this function doesn't care what they represent,
    it just summarizes them."""
    if not readings:
        return {f"{label}_count": 0}
    return {
        f"{label}_count": len(readings),
        f"{label}_mean": round(statistics.mean(readings), 4),
        f"{label}_variance": round(statistics.variance(readings), 4) if len(readings) > 1 else 0.0,
    }


if __name__ == "__main__":
    # structural test with placeholder numbers — proves the math is
    # ordinary statistics, nothing biologically interpretive
    fake_eeg = [12.1, 12.4, 11.9, 12.6, 12.0, 12.3]
    fake_hormone = [3.2, 3.4, 3.1, 3.5]

    eeg_stats = signal_channel_stats(fake_eeg, label="eeg")
    hormone_stats = signal_channel_stats(fake_hormone, label="hormone")

    print("=== EEG stats (abstract numbers only) ===")
    print(eeg_stats)
    print("\n=== Hormone stats (abstract numbers only) ===")
    print(hormone_stats)
    print("\nThese are the ONLY values that would ever reach an art/video prompt —")
    print("no raw readings, no claim about what they mean biologically.")
