"""
ui/brain_display.py

Design doc section 12: "A stylized brain/neural graphic. It can
animate during processing."

Pure SVG + CSS keyframes, no JS. It's just markup — st.html re-renders
it every rerun like anything else, and the CSS animations simply
restart, which reads fine (it's an idle/active loop, not a one-shot).
Colors come from currentColor so they inherit --bs-accent from the
global stylesheet without any extra wiring here.
"""

from __future__ import annotations

import streamlit as st

_SVG_TEMPLATE = """
<div class="bs-brain-wrap" style="display:flex;justify-content:center;padding:0.5rem 0 1rem;">
<style>
.bs-brain {{
    --spin-duration: 22s;
    --pulse-duration: 3.4s;
    color: var(--bs-accent);
    filter: drop-shadow(0 0 6px rgba(77,216,192,0.35));
}}
.bs-brain--active {{
    --spin-duration: 5s;
    --pulse-duration: 0.9s;
    color: var(--bs-warn, #e8a23a);
    filter: drop-shadow(0 0 14px rgba(232,162,58,0.55));
}}
.bs-brain-ring {{
    transform-origin: 100px 100px;
    animation: bs-spin var(--spin-duration) linear infinite;
}}
.bs-brain-ring--rev {{
    animation-direction: reverse;
    animation-duration: calc(var(--spin-duration) * 1.6);
}}
.bs-brain-core, .bs-brain-node {{
    animation: bs-pulse var(--pulse-duration) ease-in-out infinite;
    transform-origin: center;
}}
.bs-brain-node:nth-child(3n) {{ animation-delay: 0.3s; }}
.bs-brain-node:nth-child(3n+1) {{ animation-delay: 0.6s; }}
@keyframes bs-spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes bs-pulse {{
    0%, 100% {{ opacity: 0.55; }}
    50% {{ opacity: 1; }}
}}
</style>
<svg class="bs-brain{active_class}" width="180" height="180" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <g class="bs-brain-ring" fill="none" stroke="currentColor" stroke-width="0.6" opacity="0.5">
    <circle cx="100" cy="100" r="92" stroke-dasharray="2 6"/>
  </g>
  <g class="bs-brain-ring bs-brain-ring--rev" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.35">
    <circle cx="100" cy="100" r="78" stroke-dasharray="1 4"/>
  </g>
  <g stroke="currentColor" stroke-width="1" opacity="0.55">
    <line x1="100" y1="100" x2="55" y2="55"/>
    <line x1="100" y1="100" x2="145" y2="55"/>
    <line x1="100" y1="100" x2="55" y2="145"/>
    <line x1="100" y1="100" x2="145" y2="145"/>
    <line x1="100" y1="100" x2="30" y2="100"/>
    <line x1="100" y1="100" x2="170" y2="100"/>
    <line x1="100" y1="100" x2="100" y2="25"/>
    <line x1="100" y1="100" x2="100" y2="175"/>
  </g>
  <circle class="bs-brain-node" cx="55" cy="55" r="4" fill="currentColor"/>
  <circle class="bs-brain-node" cx="145" cy="55" r="4" fill="currentColor"/>
  <circle class="bs-brain-node" cx="55" cy="145" r="4" fill="currentColor"/>
  <circle class="bs-brain-node" cx="145" cy="145" r="4" fill="currentColor"/>
  <circle class="bs-brain-node" cx="30" cy="100" r="3.5" fill="currentColor"/>
  <circle class="bs-brain-node" cx="170" cy="100" r="3.5" fill="currentColor"/>
  <circle class="bs-brain-node" cx="100" cy="25" r="3.5" fill="currentColor"/>
  <circle class="bs-brain-node" cx="100" cy="175" r="3.5" fill="currentColor"/>
  <circle class="bs-brain-core" cx="100" cy="100" r="14" fill="currentColor" opacity="0.85"/>
  <circle cx="100" cy="100" r="14" fill="none" stroke="currentColor" stroke-width="1.2"/>
</svg>
</div>
"""


def render_brain_visualization(*, active: bool = False) -> None:
    """Render the brain graphic. `active=True` while a thought is
    'processing' — faster pulse, warmer color, faster spin."""
    st.html(_SVG_TEMPLATE.format(active_class=" bs-brain--active" if active else ""))
