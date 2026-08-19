"""
ui/metrics_panel.py

Design doc section 11 ("Dynamic Neural Metrics"):
NEURONS ACTIVE, SYNAPTIC LOAD, MEMORY ALLOCATION,
THOUGHT COHERENCE, COGNITIVE STABILITY, COGNITIVE DRIFT

Renders whichever subset of those it's given as a responsive stat
grid (ui.styles.stat_grid_html) — cards wrap on narrow viewports and
values are never truncated. Works with both shapes core/ produces:
- core.fake_metrics.generate_live_metric_snapshot() -> dict with
  up to 6 keys, used during the fake processing sequence.
- core.models.AnalysisMetrics -> the smaller 4-field snapshot
  stamped on the final ThoughtResult.

Optional `settle_seconds`: if > 0, the panel first flickers through
scrambled values ("still computing...") for that long, then locks
onto the real ones. Used by the FINAL ANALYSIS for drama.
"""

from __future__ import annotations

import random
import time
from typing import Any

import streamlit as st

from ui.scroll import autoscroll
from ui.styles import panel, stat_grid_html

# (dict/attr key) -> display label. Order here is display order.
_FIELD_LABELS: list[tuple[str, str]] = [
    ("neurons_active", "Neurons Active"),
    ("neuron_count", "Neurons Active"),
    ("synaptic_load", "Synaptic Load"),
    ("memory_allocation", "Memory Allocation"),
    ("memory_usage", "Memory Allocation"),
    ("thought_coherence", "Thought Coherence"),
    ("cognitive_stability", "Cognitive Stability"),
    ("cognitive_drift", "Cognitive Drift"),
]


def _get(source: Any, key: str):
    if isinstance(source, dict):
        return source.get(key)
    return getattr(source, key, None)


def _format_value(key: str, value: Any) -> str:
    if value is None:
        return "—"
    if key in ("neurons_active", "neuron_count"):
        return f"{int(value):,}"
    return f"{value}%"


def _scramble(value: str) -> str:
    """A fake 'still computing' variant of an already-formatted value."""
    if value.endswith("%"):
        return f"{random.uniform(1.0, 99.9):.1f}%"
    if value == "—":
        return value
    return f"{random.randint(1_000_000, 99_000_000):,}"


def render_metrics_panel(
    metrics: Any,
    *,
    title: str = "NEURAL METRICS",
    icon: str = "📊",
    settle_seconds: float = 0.0,
) -> None:
    """Render whichever fields are present in `metrics` as a responsive
    metric grid. Accepts a dict (live snapshot) or a pydantic model
    (AnalysisMetrics). If `settle_seconds` > 0, values flicker through
    scrambled numbers first, then lock onto the real ones."""
    seen: set[str] = set()
    rows: list[tuple[str, str]] = []
    for key, label in _FIELD_LABELS:
        if label in seen:
            continue
        value = _get(metrics, key)
        if value is None:
            continue
        rows.append((label, _format_value(key, value)))
        seen.add(label)

    if not rows:
        return

    with panel(title, icon=icon):
        slot = st.empty()
        if settle_seconds > 0:
            steps = 8
            for _ in range(steps):
                slot.html(
                    stat_grid_html(
                        [(label, _scramble(value)) for label, value in rows]
                    )
                )
                autoscroll()
                time.sleep(settle_seconds / steps)
        slot.html(stat_grid_html(rows))