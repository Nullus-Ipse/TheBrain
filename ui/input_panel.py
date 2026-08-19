"""
ui/input_panel.py

Design doc section 12:
    "WHAT WOULD YOU LIKE TO THINK ABOUT?"
    [ Type something you want your brain to think about... ]
    Primary button: "INITIATE COGNITIVE PROCESSING"
"""

from __future__ import annotations

import streamlit as st

from core.config import MAX_INPUT_LENGTH, MIN_INPUT_LENGTH
from ui.styles import panel, section_label


def render_input_panel(*, disabled: bool = False) -> tuple[str, bool]:
    """Render the input form. Returns (user_input, submitted).

    `disabled=True` greys out the button (used during cooldown / while
    a thought is already processing) without the caller needing to
    know anything about how the form is built.
    """
    with panel("INPUT", icon="🧠"):
        section_label("WHAT WOULD YOU LIKE TO THINK ABOUT?")
        with st.form("thought_form", border=False, clear_on_submit=False):
            user_input = st.text_area(
                "thought input",
                placeholder="Type something you want your brain to think about...",
                max_chars=MAX_INPUT_LENGTH,
                height=100,
                label_visibility="collapsed",
            )
            st.html(
                f'<div class="bs-dim" style="font-size:0.7rem;text-align:right;'
                f'margin-top:-0.4rem;">min {MIN_INPUT_LENGTH} · max {MAX_INPUT_LENGTH} characters</div>'
            )
            submitted = st.form_submit_button(
                "INITIATE COGNITIVE PROCESSING",
                type="primary",
                use_container_width=True,
                disabled=disabled,
            )

    return user_input or "", submitted
