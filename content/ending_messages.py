"""
content/ending_messages.py

Display copy for each ending_type (design doc section 9). This is
separate from the JSON `ending.message` field Gemini/fallback
generates per-request — these are the fixed headline/label strings the
UI can show around that generated content (e.g. a big "THOUGHT LOST"
banner above the model's own message).

core.fallback prefers this file automatically when present, picking a
random variant from each list so repeated fallbacks don't all read
identically. If this file is absent, core.fallback uses its own small
built-in default.
"""

from __future__ import annotations

ENDING_MESSAGES: dict[str, list[dict[str, str]]] = {
    "thought_lost": [
        {
            "headline": "THOUGHT LOST",
            "message": "Original thought could not be recovered.",
        },
        {
            "headline": "THOUGHT LOST",
            "message": "Original thought no longer available.",
        },
        {
            "headline": "THOUGHT LOST",
            "message": "The thought has been misplaced somewhere in memory.",
        },
    ],
    "cognitive_drift": [
        {
            "headline": "COGNITIVE DRIFT DETECTED",
            "message": "The thought has drifted well past its original topic.",
        },
        {
            "headline": "COGNITIVE DRIFT DETECTED",
            "message": "Current thought bears little resemblance to the input.",
        },
    ],
    "cognitive_loop": [
        {
            "headline": "COGNITIVE LOOP DETECTED",
            "message": "The thought has returned to something already encountered.",
        },
        {
            "headline": "COGNITIVE LOOP DETECTED",
            "message": "This thought has been had before. The brain did not notice.",
        },
    ],
    "useless_insight": [
        {
            "headline": "GENUINE INSIGHT DETECTED",
            "message": "Practical usefulness: not guaranteed.",
        },
        {
            "headline": "GENUINE INSIGHT DETECTED",
            "message": "Peer review pending. Peer review will not happen.",
        },
    ],
    "unexpectedly_useful": [
        {
            "headline": "ERROR",
            "message": "Thought became unexpectedly useful.",
        },
        {
            "headline": "ERROR",
            "message": "Accidental usefulness detected. This was not supposed to happen.",
        },
    ],
}
