"""
ui/global_stats_panel.py

Design doc section 13 ("Global Statistics"): THOUGHTS PROCESSED,
THOUGHTS LOST, AVERAGE COGNITIVE DRIFT, NEURONS WASTED, USEFUL
THOUGHTS. Entirely fictional, no database — core.fake_stats already
handles the (in-memory, per-session) bookkeeping; this module just
displays whatever it returns, as a responsive wrapping grid so giant
numbers are never truncated (they wrap + shrink via clamp() instead).
"""

from __future__ import annotations

import streamlit as st

from core.fake_stats import get_global_stats
from ui.styles import format_big_number, panel, stat_grid_html


def render_global_stats() -> None:
    stats = get_global_stats()
    rows = [
        ("Thoughts Processed", format_big_number(stats["thoughts_processed"])),
        ("Thoughts Lost", format_big_number(stats["thoughts_lost"])),
        ("Avg Cognitive Drift", f"{stats['average_cognitive_drift']}%"),
        ("Neurons Wasted", format_big_number(stats["neurons_wasted"])),
        ("Useful Thoughts", str(stats["useful_thoughts"])),
    ]
    with panel("GLOBAL COGNITIVE STATISTICS", icon="🌐"):
        st.html(stat_grid_html(rows))