"""
core/fake_stats.py

Fake global statistics (design doc section 13). These are entirely
fictional and don't require a database — per the spec, if the hosting
environment resets them, nothing is lost, because they were never real.

Implementation: seeded plausible baselines + an in-memory counter that
increments each time this process handles a thought. Backed by
st.session_state when available so numbers persist across reruns
within a user's session; falls back to a plain module-level dict
outside of Streamlit (e.g. for tests).
"""

from __future__ import annotations

import random

try:
    import streamlit as st

    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False

_STATE_KEY = "_brain_sim_fake_stats"

# Large plausible baselines so the counters look legit from the very
# first page load, before any real increments happen.
_BASELINE = {
    "thoughts_processed": 18_492_731,
    "thoughts_lost": 18_491_203,
    "neurons_wasted": 6_734_920_182_441,
}


def _get_store() -> dict:
    if _HAS_STREAMLIT:
        try:
            if _STATE_KEY not in st.session_state:
                st.session_state[_STATE_KEY] = dict(_BASELINE)
            return st.session_state[_STATE_KEY]
        except Exception:
            pass
    # Outside a Streamlit runtime, fall back to a module-level dict.
    global _fallback_store
    try:
        return _fallback_store
    except NameError:
        _fallback_store = dict(_BASELINE)
        return _fallback_store


def record_thought(ending_type: str) -> None:
    """Call once per completed thought to bump the counters."""
    store = _get_store()
    store["thoughts_processed"] += 1
    if ending_type == "thought_lost":
        store["thoughts_lost"] += 1
    store["neurons_wasted"] += random.randint(1_000_000, 90_000_000)


def get_global_stats() -> dict[str, object]:
    """Return the current fake stats, plus a couple of derived display values."""
    store = _get_store()
    return {
        "thoughts_processed": store["thoughts_processed"],
        "thoughts_lost": store["thoughts_lost"],
        "neurons_wasted": store["neurons_wasted"],
        "average_cognitive_drift": round(random.uniform(78, 92), 1),
        "useful_thoughts": "Probably 3",
    }
