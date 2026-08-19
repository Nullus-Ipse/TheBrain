"""
ui/header.py

Design doc section 12: "Header — COGNITIVE ENGINE / Subtitle: Neural
Thought Processing Interface."
"""

from __future__ import annotations

import streamlit as st

from ui.styles import COLOR_ACCENT, status_dot


def render_header() -> None:
    left, right = st.columns([3, 1], vertical_alignment="center")

    with left:
        st.html(
            '<div style="font-family:\'Orbitron\',monospace;font-weight:800;'
            f'font-size:2.1rem;letter-spacing:0.06em;color:{COLOR_ACCENT};'
            f'text-shadow:0 0 18px rgba(77,216,192,0.45);line-height:1.1;">'
            "COGNITIVE ENGINE</div>"
            '<div class="bs-dim" style="font-size:0.85rem;letter-spacing:0.08em;'
            'margin-top:0.15rem;">Neural Thought Processing Interface</div>'
        )

    with right:
        status_dot("System Online")

    st.write("")
