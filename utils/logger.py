"""
utils/logger.py

Design doc section 16: "Technical errors should still be logged
privately for debugging" — the user only ever sees the comedic
error copy from core.errors; the real exception goes here instead.

Usage:
    from utils.logger import get_logger
    log = get_logger(__name__)
    log.warning("Gemini call failed: %s", exc)
"""

from __future__ import annotations

import logging
import os

_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    root = logging.getLogger("brain_simulator")
    root.setLevel(level)
    root.propagate = False
    if not root.handlers:
        root.addHandler(handler)


def get_logger(name: str = "brain_simulator") -> logging.Logger:
    """A logger under the 'brain_simulator' namespace with one
    consistent stream handler. Safe to call repeatedly — configures
    the underlying root only once per process.

    Never log raw user input or API keys here — this is meant for
    technical failure detail (stack traces, status codes), not a
    record of what anyone typed into the brain.
    """
    _configure_root()
    if name == "brain_simulator":
        return logging.getLogger(name)
    return logging.getLogger(f"brain_simulator.{name}")
