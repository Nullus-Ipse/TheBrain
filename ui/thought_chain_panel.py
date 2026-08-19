"""
ui/thought_chain_panel.py

Design doc section 7/8: renders the thought_chain — a sequence that
starts strongly related to the input and drifts, with relevance
trending downward. Rendered as a responsive CSS grid (not st.columns,
not a rigid flex row) so long thoughts wrap inside the panel and the
relevance bar + % drop onto a second line on narrow/mobile viewports.
Layout lives in ui/styles.py (.bs-chain-* classes); this file only
fills in content + per-relevance colors.
"""

from __future__ import annotations

import streamlit as st

from core.models import ThoughtChainItem
from ui.styles import COLOR_ACCENT, COLOR_DANGER, COLOR_WARN, panel


def _relevance_color(relevance: float) -> str:
    if relevance >= 60:
        return COLOR_ACCENT
    if relevance >= 25:
        return COLOR_WARN
    return COLOR_DANGER


def render_thought_chain(thought_chain: list[ThoughtChainItem]) -> None:
    with panel("THOUGHT ASSOCIATION CHAIN", icon="🔗"):
        for i, item in enumerate(thought_chain):
            color = _relevance_color(item.relevance)
            st.html(f"""
<div class="bs-chain-row">
  <div class="bs-chain-thought" style="color:{color};text-shadow:0 0 8px {color}55;">
    {item.thought}
  </div>
  <div class="bs-chain-bar">
    <div style="width:{item.relevance}%;background:{color};box-shadow:0 0 8px {color}88;"></div>
  </div>
  <div class="bs-chain-pct bs-dim">{item.relevance:.0f}%</div>
</div>
""")
            if i < len(thought_chain) - 1:
                st.html(
                    '<div style="text-align:left;padding-left:0.15rem;" class="bs-dim">'
                    "↓</div>"
                )