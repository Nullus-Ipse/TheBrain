"""
core/config.py

All configuration lives here: Gemini connection settings, outcome
probability weights, and input limits.

Secret resolution order (so local dev and Streamlit Community Cloud
both work with zero code changes):

    1. st.secrets["KEY"]          (Streamlit Cloud secrets.toml, or a
                                    local .streamlit/secrets.toml)
    2. os.environ["KEY"]          (a real environment variable, OR one
                                    loaded from a local .env file via
                                    python-dotenv)
    3. the `default` you pass in

Locally you keep a `.env`. On Streamlit Community Cloud you set
secrets in the dashboard (or `.streamlit/secrets.toml`). Either way,
every other module in core/ just imports the constants below and
never has to know which source it came from.

Gemini models are intentionally NOT configurable through the
environment. The application is restricted to:

    1. Gemini 3.5 Flash-Lite — primary
    2. Gemini 3.1 Flash-Lite — fallback
"""

from __future__ import annotations

import os

# --- Load .env for local development, if python-dotenv is installed. ---
# This is a no-op (and never raises) when there's no .env file, and a
# no-op when python-dotenv isn't installed at all — Streamlit Cloud
# doesn't need it since secrets.toml is handled separately.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# --- Streamlit secrets are only available inside a Streamlit runtime. ---
# Importing streamlit is safe even outside `streamlit run` (e.g. in
# tests, or when core/ is imported by a script), but accessing
# st.secrets without a secrets.toml anywhere raises. We guard both.
try:
    import streamlit as st

    _HAS_STREAMLIT = True
except ImportError:
    _HAS_STREAMLIT = False


def get_setting(key: str, default: str | None = None) -> str | None:
    """Resolve a setting: st.secrets -> environment -> default.

    Every lookup is independent, so you can mix sources (e.g. keep the
    API key in Streamlit secrets but override other settings via a local
    environment variable) without anything breaking.
    """
    if _HAS_STREAMLIT:
        try:
            if key in st.secrets:
                return st.secrets[key]
        except Exception:
            # st.secrets raises StreamlitSecretNotFoundError (or similar)
            # when no secrets.toml exists at all. That's a normal local
            # setup, not an error — just fall through to os.environ.
            pass

    return os.environ.get(key, default)


def _get_int(key: str, default: int) -> int:
    try:
        return int(get_setting(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_float(key: str, default: float) -> float:
    try:
        return float(get_setting(key, str(default)))
    except (TypeError, ValueError):
        return default


def _get_bool(key: str, default: bool) -> bool:
    raw = get_setting(key, str(default))

    if isinstance(raw, bool):
        return raw

    return str(raw).strip().lower() in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Google Gemini settings
# ---------------------------------------------------------------------------

GOOGLE_API_KEY: str = get_setting("GOOGLE_API_KEY", "") or ""

# ---------------------------------------------------------------------------
# Gemini model chain
#
# These are intentionally hard-coded.
# Do NOT read them from .env or Streamlit secrets.
#
# Primary:
#   Gemini 3.5 Flash-Lite
#
# Fallback:
#   Gemini 3.1 Flash-Lite
# ---------------------------------------------------------------------------

GEMINI_PRIMARY_MODEL: str = "gemini-3.5-flash-lite"
GEMINI_FALLBACK_MODEL: str = "gemini-3.1-flash-lite"

GEMINI_TIMEOUT: int = _get_int("GEMINI_TIMEOUT", 30)
MAX_OUTPUT_TOKENS: int = _get_int("MAX_OUTPUT_TOKENS", 1024)
TEMPERATURE: float = _get_float("TEMPERATURE", 0.8)

GEMINI_API_BASE: str = get_setting(
    "GEMINI_API_BASE",
    "https://generativelanguage.googleapis.com/v1beta",
)


# ---------------------------------------------------------------------------
# Input limits
# ---------------------------------------------------------------------------

MIN_INPUT_LENGTH: int = _get_int("MIN_INPUT_LENGTH", 3)
MAX_INPUT_LENGTH: int = _get_int("MAX_INPUT_LENGTH", 250)


# ---------------------------------------------------------------------------
# Outcome probability weights — Python's alone to touch these.
# Gemini never sees the weights, only the single outcome already chosen.
# ---------------------------------------------------------------------------

OUTCOME_FAMILY_WEIGHTS: dict[str, int] = {
    "trash": 80,
    "insight": 20,
}

TRASH_ENDING_WEIGHTS: dict[str, int] = {
    "thought_lost": 55,
    "cognitive_drift": 30,
    "cognitive_loop": 15,
}

INSIGHT_ENDING_WEIGHTS: dict[str, int] = {
    "useless_insight": 92,
    "unexpectedly_useful": 8,
}


# ---------------------------------------------------------------------------
# Temp storage / fallback behavior
# ---------------------------------------------------------------------------

TEMP_DIR: str = get_setting("TEMP_DIR", "temp")

# If the Gemini call fails for any reason (missing key, timeout, quota,
# safety block, bad JSON), should thought_engine quietly degrade to a
# locally-generated fake chain (True) instead of surfacing a hard error
# (False)? Recommended True for a public deployment.
FALLBACK_MODE_ENABLED: bool = _get_bool(
    "FALLBACK_MODE_ENABLED",
    True,
)