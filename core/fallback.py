"""
core/fallback.py

Emergency result generator. Used only when:
    - Google API fails (config, timeout, quota, transport)
    - Gemini's response fails JSON validation
    - Gemini blocks the request/response on safety grounds

This does NOT try to be as good as Gemini. It exists so the site stays
funny (per the design doc: "This is not as good as Gemini, but it
keeps the site alive") instead of showing a dead end.

Note on content/fallback_insights.py:
    The design doc keeps the static insight list in
    content/fallback_insights.py. This build is core/ only, so a small
    inline list is used as a default; if content/fallback_insights.py
    exists and exports FALLBACK_INSIGHTS, that's used instead.
"""

from __future__ import annotations

import random

from core.fake_metrics import generate_analysis_metrics
from core.models import AnalysisMetrics, Ending, Insight, ThoughtChainItem, ThoughtResult

try:  # pragma: no cover - optional content/ package
    from content.fallback_insights import FALLBACK_INSIGHTS as _CONTENT_FALLBACK_INSIGHTS
except ImportError:
    _CONTENT_FALLBACK_INSIGHTS = None

try:  # pragma: no cover - optional content/ package
    from content.ending_messages import ENDING_MESSAGES as _CONTENT_ENDING_MESSAGES
except ImportError:
    _CONTENT_ENDING_MESSAGES = None

_DEFAULT_FALLBACK_INSIGHTS = [
    "A door is just a wall that got promoted.",
    "If you close your eyes, the room becomes shy.",
    "Every spoon is a tiny shovel for soup.",
    "Silence is just volume that gave up.",
    "A shadow is a reflection that took the day off.",
]

FALLBACK_INSIGHTS: list[str] = _CONTENT_FALLBACK_INSIGHTS or _DEFAULT_FALLBACK_INSIGHTS

# Generic drift vocabulary — deliberately unrelated to any real semantics,
# since a local fallback has no model to draw genuine associations from.
_DRIFT_WORDS = [
    "a related idea",
    "a tangential concept",
    "something adjacent",
    "a loosely connected memory",
    "an unrelated tangent",
    "background noise",
    "static",
    "white noise",
]

_ENDING_MESSAGES: dict[str, str] = {
    "thought_lost": "Original thought no longer available.",
    "cognitive_drift": "Cognitive drift detected. Original topic no longer relevant.",
    "cognitive_loop": "Cognitive loop detected.",
    "useless_insight": "GENUINE INSIGHT DETECTED",
    "unexpectedly_useful": "ERROR — thought became unexpectedly useful.",
}

_HARMLESS_USEFUL_THOUGHTS = [
    "Drink some water.",
    "Stretch your neck.",
    "Take a breath.",
    "Maybe close some browser tabs.",
]


def _build_chain(user_input: str, ending_type: str) -> list[ThoughtChainItem]:
    seed_word = (user_input.strip().split() or ["thought"])[0].lower()
    words = [seed_word] + random.sample(_DRIFT_WORDS, k=min(5, len(_DRIFT_WORDS)))

    if ending_type == "cognitive_loop" and len(words) >= 2:
        # Echo the seed word at the end to visualize the loop.
        words.append(seed_word)

    n = len(words)
    chain: list[ThoughtChainItem] = []
    for i, word in enumerate(words):
        # Roughly linear decay from 100 down to ~5, with a touch of jitter.
        base = 100 - (95 * i / max(1, n - 1))
        relevance = max(0.0, min(100.0, base + random.uniform(-4, 4)))
        chain.append(ThoughtChainItem(thought=word, relevance=round(relevance, 1)))

    # Guarantee the monotonic-ish trend the schema expects.
    chain.sort(key=lambda item: item.relevance, reverse=True)
    return chain


def _pick_ending_message(ending_type: str) -> str:
    """Prefer a random variant's "message" from content.ending_messages;
    fall back to the single built-in string when that file isn't present."""
    if _CONTENT_ENDING_MESSAGES and ending_type in _CONTENT_ENDING_MESSAGES:
        variant = random.choice(_CONTENT_ENDING_MESSAGES[ending_type])
        return variant["message"]
    return _ENDING_MESSAGES.get(ending_type, "The brain has stopped cooperating.")


def _build_ending(ending_type: str) -> Ending:
    message = _pick_ending_message(ending_type)

    if ending_type == "useless_insight":
        return Ending(
            type=ending_type,
            message=message,
            insight=Insight(
                text=random.choice(FALLBACK_INSIGHTS),
                confidence=round(random.uniform(70, 95), 1),
                practical_usefulness=round(random.uniform(0.0, 1.0), 1),
                scientific_validity="Pending",
            ),
        )

    if ending_type == "unexpectedly_useful":
        return Ending(
            type=ending_type,
            message=message,
            insight=Insight(
                text=random.choice(_HARMLESS_USEFUL_THOUGHTS),
                confidence=round(random.uniform(60, 80), 1),
                practical_usefulness=round(random.uniform(50, 90), 1),
                scientific_validity="Pending",
            ),
        )

    return Ending(type=ending_type, message=message, insight=None)


def generate_fallback_result(user_input: str, outcome: dict[str, str]) -> ThoughtResult:
    """Build a ThoughtResult locally, without calling Gemini.

    `outcome` is whatever core.prompt_selector.choose_cognitive_outcome()
    returned — the fallback still honors Python's chosen ending_type, it
    just writes duller content for it than Gemini would.
    """
    ending_type = outcome["ending_type"]

    analysis: AnalysisMetrics = generate_analysis_metrics()
    chain = _build_chain(user_input, ending_type)
    ending = _build_ending(ending_type)

    return ThoughtResult(
        input=user_input,
        analysis=analysis,
        thought_chain=chain,
        ending=ending,
        used_fallback=True,
    )
