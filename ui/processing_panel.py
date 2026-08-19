"""
ui/processing_panel.py

Design doc section 10 ("Fake Neural Processing") + section 12
("Processing Display: large diagnostic panel containing fake neural
metrics, current processing state, thought associations, cognitive
drift, system messages").

This module owns the *performance*, not the outcome. It plays an
intro burst of diagnostic lines, calls whatever real (possibly slow,
possibly failing) function it's handed in the middle, then plays an
outro burst once that call returns — so the animation always looks
complete regardless of how long Gemini actually took.

ui/ never imports core.thought_engine directly (that's page.py's
job, per the "Python = director" boundary) — this module just takes
a plain callable and runs it.
"""

from __future__ import annotations

import random
import time
from typing import Callable, TypeVar

import streamlit as st
from content.loading_messages import get_processing_sequence
from core.fake_metrics import generate_live_metric_snapshot
from ui.brain_display import render_brain_visualization
from ui.metrics_panel import render_metrics_panel
from ui.styles import panel

T = TypeVar("T")

_INTRO_FRACTION = 0.4  # portion of lines played before the real call


def _format_line(
    line: str,
    *,
    neuron_count: int,
    irrelevant_memory_count: int,
    integrity: int,
) -> str:
    try:
        return line.format(
            neuron_count=f"{neuron_count:,}",
            irrelevant_memory_count=irrelevant_memory_count,
            integrity=integrity,
        )
    except (KeyError, IndexError):
        return line


def run_processing_sequence(process_fn: Callable[[], T], *, brain_slot=None) -> T:
    """Play the fake diagnostic sequence and call `process_fn()` partway
    through. Returns process_fn()'s return value. Any exception raised
    by process_fn is left to propagate after the animation finishes
    (the caller decides how to render the failure).

    Pass an existing `st.empty()` as `brain_slot` (e.g. one the page
    already rendered the idle brain into) so the visualization
    transitions idle -> active -> idle in place instead of a second
    graphic appearing lower on the page. If omitted, one is created
    here for standalone use.
    """

    lines = get_processing_sequence()

    line_context = dict(
        neuron_count=random.randint(8_000_000, 90_000_000),
        irrelevant_memory_count=random.randint(500, 9000),
        integrity=random.randint(4, 22),
    )

    rendered_lines = [
        _format_line(line, **line_context)
        for line in lines
    ]

    split = max(1, int(len(rendered_lines) * _INTRO_FRACTION))
    intro, outro = rendered_lines[:split], rendered_lines[split:]

    if brain_slot is None:
        brain_slot = st.empty()

    with brain_slot.container():
        render_brain_visualization(active=True)

    with panel("NEURAL PROCESSING SEQUENCE", icon="⚙️"):
        progress_slot = st.empty()
        metrics_slot = st.empty()
        log_slot = st.empty()

        shown: list[str] = []
        total_steps = len(rendered_lines) + 1  # +1 for the real call itself

        def _tick(step: int) -> None:
            progress_slot.progress(
                min(1.0, step / total_steps),
                text=(
                    f"COGNITIVE LOAD "
                    f"{min(100, int(step / total_steps * 100))}%"
                ),
            )

            with metrics_slot.container():
                render_metrics_panel(
                    generate_live_metric_snapshot(),
                    title="LIVE READOUT",
                    icon="📡",
                )

            log_text = "\n".join(
                f"> {line}"
                for line in shown[-9:]
            )

            log_slot.code(
                log_text or "> ...",
                language=None,
            )

        # ---------------------------------------------------------
        # INTRO DIAGNOSTICS
        # ---------------------------------------------------------

        for i, line in enumerate(intro, start=1):
            shown.append(line)
            _tick(i)
            time.sleep(random.uniform(0.08, 0.2))

        # ---------------------------------------------------------
        # GEMINI CONTACT
        # ---------------------------------------------------------

        shown.append("Contacting Gemini cognitive substrate...")
        _tick(len(intro) + 1)

        # ---------------------------------------------------------
        # REAL COGNITIVE PROCESSING
        # ---------------------------------------------------------

        try:
            result = process_fn()
        finally:
            pass

        # ---------------------------------------------------------
        # OUTRO DIAGNOSTICS
        # ---------------------------------------------------------

        for j, line in enumerate(outro, start=1):
            shown.append(line)
            _tick(len(intro) + 1 + j)
            time.sleep(random.uniform(0.05, 0.12))

        # ---------------------------------------------------------
        # COMPLETE
        # ---------------------------------------------------------

        progress_slot.progress(
            1.0,
            text="COGNITIVE LOAD 100%",
        )

    # Return the brain visualization to its idle state.
    brain_slot.empty()

    with brain_slot.container():
        render_brain_visualization(active=False)

    return result