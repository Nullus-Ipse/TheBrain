"""
utils/numbers.py

Formatting and small numeric helpers shared by anything that displays
or generates the app's many fake numbers (neuron counts, relevance
scores, global stats).
"""

from __future__ import annotations

import random


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    """Restrict `value` to [lo, hi]. Used wherever a generated number
    (e.g. relevance from Gemini) needs to be trustworthy even if the
    source wasn't."""
    return max(lo, min(hi, value))


def format_big_number(n: int | float) -> str:
    """1234567 -> '1,234,567'. Falls back to str(n) for anything that
    can't be coerced to int (keeps display code from crashing on
    unexpected input)."""
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def format_percent(value: float, *, decimals: int = 1) -> str:
    """82.4 -> '82.4%'."""
    return f"{value:.{decimals}f}%"


def jitter(value: float, spread: float, *, lo: float = 0.0, hi: float = 100.0) -> float:
    """`value` nudged by a random amount in [-spread, spread], clamped
    to [lo, hi]. Used for the 'live' fluctuating metric readouts so
    consecutive frames feel like they're wobbling around a real
    number rather than jumping randomly."""
    return clamp(value + random.uniform(-spread, spread), lo, hi)
