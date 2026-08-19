"""
ui/page.py

The entry point for this whole package. app.py should be able to be
just:

    import streamlit as st
    from ui.page import render_page

    render_page()

Everything else in ui/ is a building block this function assembles.
This is also the one place in ui/ that talks to core.thought_engine —
per the design doc's "Python = director" boundary, the rest of ui/
only ever receives a ThoughtResult or an error_code, it never decides
outcomes or calls Gemini itself.
"""

from __future__ import annotations

import time

import streamlit as st

from core.errors import BrainSimulatorError
from core.thought_engine import process_thought
from ui.brain_display import render_brain_visualization
from ui.footer import render_footer
from ui.global_stats_panel import render_global_stats
from ui.header import render_header
from ui.input_panel import render_input_panel
from ui.processing_panel import run_processing_sequence
from ui.result_panel import render_error_result, render_result
from ui.scroll import autoscroll
from ui.styles import inject_global_styles

# Minimal client-side abuse guard (design doc section: "Add cooldown in
# st.session_state"). This is a UX nicety, not real rate limiting —
# actual abuse protection belongs at Google's quota level / a reverse
# proxy, per the doc's own caveat that "Streamlit is not amazing at
# serious rate limiting."
THINK_COOLDOWN_SECONDS = 3.0

_STATE_DEFAULTS = {
    "bs_last_think_ts": 0.0,
    "bs_last_result": None,
    "bs_last_error": None,
}


def _init_state() -> None:
    for key, default in _STATE_DEFAULTS.items():
        st.session_state.setdefault(key, default)


def render_page() -> None:
    st.set_page_config(
        page_title="Cognitive Engine",
        page_icon="🧠",
        layout="centered",
    )
    inject_global_styles()
    _init_state()

    render_header()

    brain_slot = st.empty()
    with brain_slot.container():
        render_brain_visualization(active=False)

    render_global_stats()
    st.write("")

    cooling_down = (
        time.monotonic() - st.session_state["bs_last_think_ts"]
    ) < THINK_COOLDOWN_SECONDS

    user_input, submitted = render_input_panel(disabled=cooling_down)

    if cooling_down:
        st.caption("🌀 SYSTEM COOLING DOWN — give the brain a second to recover.")

    if submitted and not cooling_down:
        st.session_state["bs_last_think_ts"] = time.monotonic()
        st.session_state["bs_last_result"] = None
        st.session_state["bs_last_error"] = None
        try:
            result = run_processing_sequence(
                lambda: process_thought(user_input), brain_slot=brain_slot
            )
            st.session_state["bs_last_result"] = result
        except BrainSimulatorError as exc:
            st.session_state["bs_last_error"] = exc.error_code

    st.write("")

    if st.session_state["bs_last_error"]:
        render_error_result(st.session_state["bs_last_error"])
        autoscroll()  # <--- snap to the failure panel
    elif st.session_state["bs_last_result"] is not None:
        render_result(st.session_state["bs_last_result"])
        autoscroll()  # <--- snap to the final punchline

    render_footer()