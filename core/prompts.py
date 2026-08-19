"""
core/prompts.py

Builds the actual prompt text sent to Gemini. Python has already
decided the outcome (core.prompt_selector) — these builders exist
only to phrase that decision as an instruction the model can't wiggle
out of.

Note on content/ai_examples.py:
    The design doc puts the few-shot JSON examples in
    content/ai_examples.py. Since this build is core/ only, the
    examples are inlined below as _FALLBACK_TRASH_EXAMPLE /
    _FALLBACK_INSIGHT_EXAMPLE. If content/ai_examples.py exists and
    exports TRASH_EXAMPLE / INSIGHT_EXAMPLE, those are used instead —
    so nothing here needs to change later.
"""

from __future__ import annotations

try:  # pragma: no cover - optional content/ package
    from content.ai_examples import INSIGHT_EXAMPLE as _CONTENT_INSIGHT_EXAMPLE
    from content.ai_examples import TRASH_EXAMPLE as _CONTENT_TRASH_EXAMPLE
except ImportError:
    _CONTENT_TRASH_EXAMPLE = None
    _CONTENT_INSIGHT_EXAMPLE = None

_FALLBACK_TRASH_EXAMPLE = """{
  "input": "Should I buy a new car?",
  "analysis": {
    "neuron_count": 36739784,
    "synaptic_load": 82.4,
    "memory_usage": 64.2,
    "cognitive_stability": 31.8
  },
  "thought_chain": [
    {"thought": "car", "relevance": 100},
    {"thought": "vehicle", "relevance": 91},
    {"thought": "road", "relevance": 77},
    {"thought": "traffic", "relevance": 61},
    {"thought": "red light", "relevance": 38},
    {"thought": "apple", "relevance": 16},
    {"thought": "banana", "relevance": 6}
  ],
  "ending": {
    "type": "thought_lost",
    "message": "Original thought no longer available."
  }
}"""

_FALLBACK_INSIGHT_EXAMPLE = """{
  "input": "What should I have for dinner?",
  "analysis": {
    "neuron_count": 29182456,
    "synaptic_load": 77.1,
    "memory_usage": 58.9,
    "cognitive_stability": 22.4
  },
  "thought_chain": [
    {"thought": "dinner", "relevance": 100},
    {"thought": "food", "relevance": 92},
    {"thought": "plate", "relevance": 79},
    {"thought": "circle", "relevance": 63},
    {"thought": "moon", "relevance": 41},
    {"thought": "cheese", "relevance": 22},
    {"thought": "mouse", "relevance": 9}
  ],
  "ending": {
    "type": "useless_insight",
    "message": "GENUINE INSIGHT DETECTED",
    "insight": {
      "text": "The moon is only a snack because no one has tried to eat it seriously enough.",
      "confidence": 91.4,
      "practical_usefulness": 0.2,
      "scientific_validity": "Pending"
    }
  }
}"""

TRASH_EXAMPLE = _CONTENT_TRASH_EXAMPLE or _FALLBACK_TRASH_EXAMPLE
INSIGHT_EXAMPLE = _CONTENT_INSIGHT_EXAMPLE or _FALLBACK_INSIGHT_EXAMPLE


_SHARED_RULES = """Rules:
1. Return ONLY a raw JSON object.
2. Do not include markdown, code fences, or explanations.
3. Do not answer the user's question directly.
4. Create 6 to 12 thought-chain items.
5. The first thought must be strongly related to the user input.
6. Each thought should be understandable but increasingly distant.
7. Relevance must start near 100 and decrease over time (the last
   item's relevance must be lower than the first item's).
8. The ending type must be exactly "{ending_type}".
9. The tone should be comedic but safe.
10. Do not include medical, legal, financial, emotional, or self-harm
    advice anywhere in the output.
"""

_TRASH_TEMPLATE = """You are the Cognitive Engine of a comedic fake brain simulator.

Your job is not to answer the user's question. Your job is to generate
a structured JSON object representing a thought chain that starts
related to the user's input and gradually drifts into absurdity,
ending in "{ending_type}".

User thought:
{user_input}

Required ending type:
{ending_type}

{shared_rules}
Additional rule for this ending type:
{ending_specific_rule}

Example output structure (for style/shape only — do not reuse its content):
{example_json}
"""

_INSIGHT_TEMPLATE = """You are the Cognitive Engine of a comedic fake brain simulator.

Your job is to generate a structured JSON object representing a
thought chain that begins related to the user's input and gradually
drifts into an absurd but connected fake insight.

User thought:
{user_input}

Required ending type:
{ending_type}

{shared_rules}
Additional rules for this ending type:
11. The final thought must naturally lead into the insight.
12. The insight must feel connected to the final thought and the
    whole chain — do not generate an insight unrelated to where the
    chain drifted. Example: if the chain drifts from fish to ocean to
    waves to washing machine to socks to missing sock, the insight
    should be about missing socks, laundry, or fabric-based
    existential loss — not something unrelated like bananas.
13. The insight must sound profound but be practically useless.
14. The insight must not be real advice of any kind.
15. Include the "insight" object inside "ending" with fields: text,
    confidence, practical_usefulness, scientific_validity.
{ending_specific_rule}

Example output structure (for style/shape only — do not reuse its content):
{example_json}
"""

_ENDING_SPECIFIC_RULES: dict[str, str] = {
    "thought_lost": (
        "The chain should trail off; the final ending.message should read "
        'like "Original thought no longer available." (your own phrasing is fine).'
    ),
    "cognitive_drift": (
        "The final thought_chain item should itself be presented as the "
        "drifted-to result; ending.message should announce the drift "
        "(e.g. include a drift percentage in the message)."
    ),
    "cognitive_loop": (
        "The last one or two thought_chain items should echo an earlier "
        "item in the chain (same or near-identical thought text), showing "
        "the thought looped back on itself; ending.message should announce "
        "the loop."
    ),
    "useless_insight": (
        "ending.message should read like an excited system announcement, "
        'e.g. "GENUINE INSIGHT DETECTED".'
    ),
    "unexpectedly_useful": (
        "The insight text must be genuinely mundane, harmless, boring "
        "advice (e.g. drink water, stretch, take a breath, close some "
        "browser tabs) — nothing that could be mistaken for real "
        'guidance on anything serious. ending.message should read like '
        '"ERROR — thought became unexpectedly useful."'
    ),
}


def build_trash_prompt(user_input: str, ending_type: str) -> str:
    shared_rules = _SHARED_RULES.format(ending_type=ending_type)
    return _TRASH_TEMPLATE.format(
        user_input=user_input,
        ending_type=ending_type,
        shared_rules=shared_rules,
        ending_specific_rule=_ENDING_SPECIFIC_RULES.get(ending_type, ""),
        example_json=TRASH_EXAMPLE,
    )


def build_insight_prompt(user_input: str, ending_type: str) -> str:
    shared_rules = _SHARED_RULES.format(ending_type=ending_type)
    return _INSIGHT_TEMPLATE.format(
        user_input=user_input,
        ending_type=ending_type,
        shared_rules=shared_rules,
        ending_specific_rule=_ENDING_SPECIFIC_RULES.get(ending_type, ""),
        example_json=INSIGHT_EXAMPLE,
    )


def build_prompt(user_input: str, outcome: dict[str, str]) -> str:
    """Dispatch to the right builder based on the family Python already chose."""
    family = outcome["family"]
    ending_type = outcome["ending_type"]

    if family == "trash":
        return build_trash_prompt(user_input, ending_type)
    if family == "insight":
        return build_insight_prompt(user_input, ending_type)

    raise ValueError(f"Unknown outcome family: {family!r}")
