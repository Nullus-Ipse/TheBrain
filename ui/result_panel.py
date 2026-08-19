"""
ui/result_panel.py

Design doc section 9 (Thought Outcomes) + section 16 (Error Handling):
renders the final banner for whichever ending_type Python chose, the
optional insight card, and — separately — the comedic error state for
anything core/ raised (bad input, or a hard failure with fallback
mode disabled).
"""

from __future__ import annotations

import random

import streamlit as st

from content.ending_messages import ENDING_MESSAGES
from core.errors import get_error_copy
from core.models import ThoughtResult
from ui.metrics_panel import render_metrics_panel
from ui.styles import COLOR_ACCENT, COLOR_DANGER, COLOR_WARN, badge, panel, stat_grid_html
from ui.thought_chain_panel import render_thought_chain

# Trash endings read as a "failure"; insight endings read as a
# (fake) triumph. unexpectedly_useful is deliberately framed as an
# ERROR per the design doc, even though the content itself is mundane
# advice — the joke is that usefulness is the malfunction.
_TONE_BY_TYPE = {
    "thought_lost": COLOR_DANGER,
    "cognitive_drift": COLOR_WARN,
    "cognitive_loop": COLOR_WARN,
    "useless_insight": COLOR_ACCENT,
    "unexpectedly_useful": COLOR_DANGER,
}

_FALLBACK_HEADLINE = {
    "thought_lost": "THOUGHT LOST",
    "cognitive_drift": "COGNITIVE DRIFT DETECTED",
    "cognitive_loop": "COGNITIVE LOOP DETECTED",
    "useless_insight": "GENUINE INSIGHT DETECTED",
    "unexpectedly_useful": "ERROR",
}


def _headline_for(ending_type: str) -> str:
    variants = ENDING_MESSAGES.get(ending_type)
    if variants:
        return random.choice(variants)["headline"]
    return _FALLBACK_HEADLINE.get(ending_type, "COGNITIVE EVENT")


def _render_banner(ending_type: str, message: str) -> None:
    color = _TONE_BY_TYPE.get(ending_type, COLOR_ACCENT)
    headline = _headline_for(ending_type)
    st.html(f"""
<div style="border:1px solid {color};border-radius:6px;padding:1rem 1.25rem;
background:linear-gradient(180deg,{color}14,transparent 60%);
box-shadow:0 0 24px {color}33;margin-bottom:0.75rem;">
  <div style="font-family:'Orbitron',monospace;font-weight:800;font-size:1.4rem;
letter-spacing:0.06em;color:{color};text-shadow:0 0 14px {color}66;">
    {headline}
  </div>
  <div class="bs-dim" style="margin-top:0.35rem;font-size:0.9rem;overflow-wrap:anywhere;">{message}</div>
</div>
""")


def _render_insight_card(insight) -> None:
    st.html(f"""
<div style="border-left:3px solid {COLOR_ACCENT};padding:0.5rem 0 0.5rem 1rem;margin:0.75rem 0;">
  <div style="font-size:1.05rem;font-style:italic;color:{COLOR_ACCENT};overflow-wrap:anywhere;">
    &ldquo;{insight.text}&rdquo;
  </div>
</div>
""")
    st.html(stat_grid_html([
        ("Confidence", f"{insight.confidence:.1f}%"),
        ("Practical Usefulness", f"{insight.practical_usefulness:.1f}%"),
        ("Scientific Validity", insight.scientific_validity),
    ]))


def render_result(result: ThoughtResult) -> None:
    ending = result.ending
    with panel("RESULT", icon="🧾"):
        if result.used_fallback:
            st.html(
                badge("⚠ Local fallback — Gemini unavailable", tone="warn")
            )
            st.write("")
        _render_banner(ending.type, ending.message)
        if ending.insight is not None:
            _render_insight_card(ending.insight)
    render_metrics_panel(
        result.analysis, title="FINAL ANALYSIS", icon="🧬", settle_seconds=1.2
    )
    render_thought_chain(result.thought_chain)


def render_error_result(error_code: str) -> None:
    """Render the comedic failure state for a core.errors.BrainSimulatorError
    subclass's error_code (design doc section 16 — errors are part of
    the experience, never a raw stack trace)."""
    copy = get_error_copy(error_code)
    color = COLOR_DANGER
    st.html(f"""
<div style="border:1px solid {color};border-radius:6px;padding:1rem 1.25rem;
background:linear-gradient(180deg,{color}14,transparent 60%);
box-shadow:0 0 24px {color}33;">
  <div style="font-family:'Orbitron',monospace;font-weight:800;font-size:1.25rem;
letter-spacing:0.06em;color:{color};text-shadow:0 0 14px {color}66;">
    {copy['title']}
  </div>
  <div class="bs-dim" style="margin-top:0.35rem;font-size:0.9rem;overflow-wrap:anywhere;">{copy['body']}</div>
</div>
""")