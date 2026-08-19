"""
ui/footer.py

Design doc section 14 (Branding / Slogans) + the spirit of section 17
(Privacy: "should clearly remain a novelty application").
"""

from __future__ import annotations

import streamlit as st

from content.slogans import get_random_slogan
from ui.styles import COLOR_TEXT_DIM


def render_footer() -> None:
    st.divider()
    slogan = get_random_slogan()
    st.html(f"""
<div style="text-align:center;color:{COLOR_TEXT_DIM};font-size:0.78rem;
     letter-spacing:0.04em;padding-bottom:1rem;">
  <div>{slogan}</div>
  <div style="opacity:0.7;margin-top:0.2rem;">
    A novelty application. Not medical, legal, or financial advice.
    Not even good advice.
  </div>
</div>
""")
