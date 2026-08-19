"""
core/fake_metrics.py

Generates the meaningless-but-convincing numbers the UI displays:
neuron counts, synaptic load, memory usage, cognitive stability, and
the fluctuating "live" readouts during the fake processing sequence.

None of this measures anything real. Per the design doc (section 11):
"Their purpose is purely aesthetic and comedic."
"""

from __future__ import annotations

import random

from core.models import AnalysisMetrics


def generate_analysis_metrics() -> AnalysisMetrics:
    """One snapshot of fake metrics for the final result payload."""
    return AnalysisMetrics(
        neuron_count=random.randint(8_000_000, 90_000_000),
        synaptic_load=round(random.uniform(40, 99), 1),
        memory_usage=round(random.uniform(30, 95), 1),
        cognitive_stability=round(random.uniform(3, 60), 1),
    )


def generate_live_metric_snapshot() -> dict[str, float | int]:
    """One frame of the fluctuating readout shown while 'processing'.

    Call this repeatedly (e.g. once per animation tick) to get numbers
    that jitter around plausibly, for ui/processing_panel.py to render.
    """
    return {
        "neurons_active": random.randint(8_000_000, 90_000_000),
        "synaptic_load": round(random.uniform(20, 100), 1),
        "memory_allocation": round(random.uniform(20, 100), 1),
        "thought_coherence": round(random.uniform(0, 100), 1),
        "cognitive_stability": round(random.uniform(0, 100), 1),
        "cognitive_drift": round(random.uniform(0, 100), 1),
    }


def generate_live_metric_sequence(n: int = 8) -> list[dict[str, float | int]]:
    """A short sequence of snapshots for a canned (non-live-loop) animation."""
    return [generate_live_metric_snapshot() for _ in range(max(1, n))]
