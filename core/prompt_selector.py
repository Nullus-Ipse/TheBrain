"""
core/prompt_selector.py

The randomness controller. This is where we do NOT trust the AI to
choose the outcome.

Python picks:
    1. outcome_family  -> "trash" | "insight"
    2. ending_type      -> the exact ending inside that family

Gemini is then told, non-negotiably, which ending_type to write toward.
"""

from __future__ import annotations

import random

from core.config import (
    INSIGHT_ENDING_WEIGHTS,
    OUTCOME_FAMILY_WEIGHTS,
    TRASH_ENDING_WEIGHTS,
)

OutcomeFamily = str  # "trash" | "insight"
EndingType = str


def _weighted_choice(weights: dict[str, int]) -> str:
    options = list(weights.keys())
    values = list(weights.values())
    return random.choices(options, weights=values, k=1)[0]


def choose_outcome_family() -> OutcomeFamily:
    return _weighted_choice(OUTCOME_FAMILY_WEIGHTS)


def choose_trash_ending() -> EndingType:
    return _weighted_choice(TRASH_ENDING_WEIGHTS)


def choose_insight_ending() -> EndingType:
    return _weighted_choice(INSIGHT_ENDING_WEIGHTS)


def choose_cognitive_outcome() -> dict[str, str]:
    """Return e.g. {"family": "trash", "ending_type": "thought_lost"}.

    This is the single call thought_engine needs — everything else in
    this module exists to support it (and to make each weighted roll
    independently testable/mockable).
    """
    family = choose_outcome_family()

    if family == "trash":
        return {"family": "trash", "ending_type": choose_trash_ending()}

    return {"family": "insight", "ending_type": choose_insight_ending()}
