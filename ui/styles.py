"""
ui/styles.py

The only file in ui/ that touches raw CSS. Everything else should
just use st.container(border=True), st.columns, st.metric, etc. and
borrow the helpers below.

Philosophy (see design doc section 15 + the "don't fight Streamlit"
rule from the person building this):
- Do NOT try to restyle Streamlit's internal DOM structure.
- DO set theme-level things (fonts, colors, glow, one background
  overlay) on stable, documented hooks: `.stApp` itself, and the
  handful of `data-testid` attributes Streamlit publishes for
  exactly this purpose (stMetric, stTextArea, stProgress, ...).
- If Streamlit's internals ever shift, the worst case is these
  rules quietly stop matching and the app degrades to plain
  Streamlit — never a broken layout.

Pairs with the optional .streamlit/config.toml (dark theme + accent
color) shipped alongside this project — that file does most of the
"looks expensive" work for free, before a single line of CSS runs.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import streamlit as st

# ---------------------------------------------------------------------------
# Palette — keep this the single source of truth for color. Everything
# below (and .streamlit/config.toml) should agree with these values.
# ---------------------------------------------------------------------------
COLOR_BG = "#05070a"
COLOR_PANEL = "#0b0f16"
COLOR_BORDER = "#1c2530"
COLOR_ACCENT = "#4dd8c0"      # cyan-green: idle / insight / "ok"
COLOR_ACCENT_DIM = "#2a6e63"
COLOR_WARN = "#e8a23a"        # amber: trash / drift
COLOR_DANGER = "#e05a5a"      # red: errors / thought lost
COLOR_TEXT = "#d7e4e0"
COLOR_TEXT_DIM = "#7d8f91"

_STYLE_KEY = "_bs_styles_injected"


def inject_global_styles() -> None:
    """Call once near the top of the page. Safe to call more than once
    (Streamlit reruns the whole script every interaction) — guarded so
    the <style> block is only emitted once per session for tidiness.
    """

    st.html(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&family=Share+Tech+Mono&display=swap');

:root {{
  --bs-bg: {COLOR_BG};
  --bs-panel: {COLOR_PANEL};
  --bs-border: {COLOR_BORDER};
  --bs-accent: {COLOR_ACCENT};
  --bs-accent-dim: {COLOR_ACCENT_DIM};
  --bs-warn: {COLOR_WARN};
  --bs-danger: {COLOR_DANGER};
  --bs-text: {COLOR_TEXT};
  --bs-text-dim: {COLOR_TEXT_DIM};
}}

/* --- App shell: background + faint grid + scanline drift --- */
.stApp {{
  background-color: var(--bs-bg);
  background-image:
    linear-gradient(rgba(77,216,192,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(77,216,192,0.05) 1px, transparent 1px);
  background-size: 34px 34px;
}}
.stApp::before {{
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.02),
    rgba(255,255,255,0.02) 1px,
    transparent 2px,
    transparent 3px
  );
  mix-blend-mode: overlay;
}}

/* --- Typography --- */
.stApp, .stApp p, .stApp li, .stApp label, .stApp span {{
  font-family: 'Share Tech Mono', ui-monospace, monospace;
  color: var(--bs-text);
}}
.stApp h1, .stApp h2, .stApp h3 {{
  font-family: 'Orbitron', ui-monospace, monospace;
  letter-spacing: 0.04em;
}}

/* --- Bordered containers (st.container(border=True)) become "panels" --- */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: linear-gradient(180deg, rgba(77,216,192,0.03), transparent 40%), var(--bs-panel);
  border-color: var(--bs-border) !important;
  border-radius: 6px !important;
}}

/* --- Metrics: technical readout look --- */
[data-testid="stMetric"] {{
  background: rgba(77,216,192,0.04);
  border: 1px solid var(--bs-border);
  border-radius: 4px;
  padding: 0.6rem 0.75rem;
}}
[data-testid="stMetricLabel"] {{
  font-family: 'Share Tech Mono', monospace !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.7rem !important;
  color: var(--bs-text-dim) !important;
}}
[data-testid="stMetricValue"] {{
  font-family: 'Share Tech Mono', monospace !important;
  color: var(--bs-accent) !important;
  text-shadow: 0 0 10px rgba(77,216,192,0.35);
}}

/* --- Inputs: terminal feel --- */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {{
  background: #060a0d !important;
  color: var(--bs-accent) !important;
  border: 1px solid var(--bs-border) !important;
  font-family: 'Share Tech Mono', monospace !important;
}}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {{
  border-color: var(--bs-accent) !important;
  box-shadow: 0 0 0 1px var(--bs-accent), 0 0 14px rgba(77,216,192,0.25) !important;
}}

/* --- Buttons --- */
.stButton > button, .stFormSubmitButton > button {{
  font-family: 'Orbitron', monospace !important;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  border-radius: 3px !important;
  transition: box-shadow 0.2s ease, transform 0.05s ease;
}}
.stButton > button:hover, .stFormSubmitButton > button:hover {{
  box-shadow: 0 0 18px rgba(77,216,192,0.45);
}}
.stButton > button:active, .stFormSubmitButton > button:active {{
  transform: translateY(1px);
}}

/* --- Progress bar glow --- */
[data-testid="stProgress"] div div {{
  background-image: linear-gradient(90deg, var(--bs-accent-dim), var(--bs-accent)) !important;
  box-shadow: 0 0 10px rgba(77,216,192,0.5);
}}

/* --- Dividers --- */
hr {{
  border-color: var(--bs-border) !important;
}}

/* --- Small helper classes used by ui/ modules --- */
.bs-dim {{ color: var(--bs-text-dim); }}
.bs-label {{
  font-family: 'Share Tech Mono', monospace;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--bs-text-dim);
  margin-bottom: 0.35rem;
}}

@keyframes bs-blink {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.25; }}
}}
.bs-status-dot {{
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--bs-accent);
  box-shadow: 0 0 8px var(--bs-accent);
  animation: bs-blink 2.2s ease-in-out infinite;
  margin-right: 0.4em;
}}

/* ===========================================================================
   RESPONSIVE STAT GRID — replaces st.columns for metric readouts.
   Cards wrap automatically: 3-across on desktop, 2 on tablet, 1-2 on
   phones. Nothing is ever truncated; long values wrap and the font
   scales with the viewport via clamp().
   =========================================================================== */
.bs-stat-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.6rem 0.9rem;
  margin-top: 0.4rem;
}}
.bs-stat {{
  background: rgba(77,216,192,0.04);
  border: 1px solid var(--bs-border);
  border-radius: 4px;
  padding: 0.6rem 0.75rem;
  min-width: 0; /* lets children shrink + wrap instead of overflowing */
}}
.bs-stat-label {{
  font-family: 'Share Tech Mono', monospace;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 0.7rem;
  color: var(--bs-text-dim);
  margin-bottom: 0.3rem;
  white-space: normal;
  overflow-wrap: anywhere;
}}
.bs-stat-value {{
  font-family: 'Share Tech Mono', monospace;
  font-size: clamp(1.05rem, 4.5vw, 1.6rem);
  line-height: 1.25;
  color: var(--bs-accent);
  text-shadow: 0 0 10px rgba(77,216,192,0.35);
  white-space: normal;
  overflow-wrap: anywhere;
}}

/* ===========================================================================
   THOUGHT CHAIN ROWS — the thought text always gets its own space and
   wraps inside the panel. On narrow screens the relevance bar + %
   drop onto a second line under the text; on wide screens it's the
   classic one-line "thought ────bar──── 42%" layout.
   =========================================================================== */
.bs-chain-row {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-areas:
    "thought thought"
    "bar     pct";
  gap: 0.35rem 0.75rem;
  align-items: center;
  padding: 0.3rem 0;
}}
.bs-chain-thought {{
  grid-area: thought;
  font-size: 0.95rem;
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
}}
.bs-chain-bar {{
  grid-area: bar;
  height: 6px;
  border-radius: 3px;
  background: rgba(255,255,255,0.06);
  overflow: hidden;
  min-width: 0;
}}
.bs-chain-bar > div {{
  height: 100%;
}}
.bs-chain-pct {{
  grid-area: pct;
  font-size: 0.72rem;
  min-width: 2.6em;
  text-align: right;
}}
@media (min-width: 720px) {{
  .bs-chain-row {{
    grid-template-columns: minmax(0, 1.2fr) minmax(80px, 0.8fr) auto;
    grid-template-areas: "thought bar pct";
  }}
}}
</style>
""")


# ---------------------------------------------------------------------------
# Small shared helpers — plain functions/components, not CSS overrides.
# Every ui/ module can import these instead of re-inventing panel chrome.
# ---------------------------------------------------------------------------
@contextmanager
def panel(title: str, *, icon: str = "") -> Iterator[None]:
    """A bordered 'diagnostic panel' with a small uppercase label header.

    Usage:
        with panel("NEURAL METRICS", icon="🧠"):
            st.metric(...)
    """
    with st.container(border=True):
        label = f"{icon}&nbsp;{title}" if icon else title
        st.html(f'<div class="bs-label">{label}</div>')
        yield


def section_label(text: str) -> None:
    st.html(f'<div class="bs-label">{text}</div>')


def status_dot(text: str, *, color: str = COLOR_ACCENT) -> None:
    st.html(
        f'<span class="bs-status-dot" style="background:{color};'
        f'box-shadow:0 0 8px {color};"></span>'
        f'<span class="bs-dim" style="font-size:0.75rem;letter-spacing:0.1em;'
        f'text-transform:uppercase;">{text}</span>'
    )


def badge(text: str, *, tone: str = "accent") -> str:
    """Return (not render) an inline badge span. Caller does st.html(...)
    so it can be composed inline with other markup."""
    colors = {
        "accent": COLOR_ACCENT,
        "warn": COLOR_WARN,
        "danger": COLOR_DANGER,
        "dim": COLOR_TEXT_DIM,
    }
    c = colors.get(tone, COLOR_ACCENT)
    return (
        f'<span style="display:inline-block;border:1px solid {c};color:{c};'
        f'border-radius:3px;padding:0.1em 0.5em;font-size:0.7rem;'
        f'letter-spacing:0.08em;text-transform:uppercase;'
        f'font-family:\'Share Tech Mono\',monospace;">{text}</span>'
    )


def stat_grid_html(stats: list[tuple[str, str]]) -> str:
    """Return (not render) a responsive stat-grid div. Caller wraps it in
    st.html(...). Replaces st.columns+st.metric so readouts wrap on
    phones and never truncate. `stats` is a list of (label, value)."""
    cells = "".join(
        f'<div class="bs-stat">'
        f'<div class="bs-stat-label">{label}</div>'
        f'<div class="bs-stat-value">{value}</div>'
        f'</div>'
        for label, value in stats
    )
    return f'<div class="bs-stat-grid">{cells}</div>'


def format_big_number(n: int | float) -> str:
    """1234567 -> '1,234,567'. Keeps things readable in the giant fake stats."""
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)