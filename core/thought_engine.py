"""
core/thought_engine.py

The conductor. This is the one function ui/ (or anything else) needs
to call: process_thought(user_input).

Flow (matches the design doc):
    1. Receive user input.
    2. Validate input length.
    3. Python chooses outcome family.
    4. Python chooses exact ending type.
    5. Python builds the prompt.
    6. Prompt is sent to Gemini.
    7. Gemini returns JSON.
    8. JSON is validated.
    9. Temporary JSON file is created.
    10. Result is returned for the caller to stash in session_state.
    11. Temporary file is deleted.
    12. (Caller) UI renders from session_state.

If step 6-8 fails for any reason and FALLBACK_MODE_ENABLED is True,
this transparently swaps in core.fallback instead of raising — the
returned ThoughtResult has `used_fallback=True` so the UI can decide
whether to mention it.
"""

from __future__ import annotations

from core.config import FALLBACK_MODE_ENABLED, MAX_INPUT_LENGTH, MIN_INPUT_LENGTH
from core.errors import (
    BrainSimulatorError,
    InputTooLongError,
    InputTooShortError,
)
from core.fallback import generate_fallback_result
from core.gemini_client import generate_json_from_gemini
from core.json_validator import validate_thought_json
from core.models import ThoughtResult
from core.prompt_selector import choose_cognitive_outcome
from core.prompts import build_prompt
from core.temp_file import create_temp_json, delete_temp_json
from core.fake_stats import record_thought


def validate_input(user_input: str) -> str:
    """Raises InputTooShortError / InputTooLongError. Returns the trimmed input."""
    trimmed = (user_input or "").strip()
    if len(trimmed) < MIN_INPUT_LENGTH:
        raise InputTooShortError("Input too short.")
    if len(trimmed) > MAX_INPUT_LENGTH:
        raise InputTooLongError("Input too long.")
    return trimmed


def process_thought(user_input: str) -> ThoughtResult:
    """Run the full pipeline for one THINK press.

    Raises:
        InputTooShortError / InputTooLongError: bad input — these are
            NOT swallowed by fallback mode, since there's no sensible
            "fallback" for an empty or oversized thought.
        BrainSimulatorError subclasses: only when FALLBACK_MODE_ENABLED
            is False and the Gemini pipeline fails.
    """
    clean_input = validate_input(user_input)
    outcome = choose_cognitive_outcome()

    result: ThoughtResult
    try:
        prompt = build_prompt(clean_input, outcome)
        raw_text = generate_json_from_gemini(prompt)
        result = validate_thought_json(raw_text, expected_ending_type=outcome["ending_type"])
        # Re-stamp input/used_fallback in case Gemini echoed the input oddly.
        result = result.model_copy(update={"input": clean_input, "used_fallback": False})
    except BrainSimulatorError:
        if not FALLBACK_MODE_ENABLED:
            raise
        result = generate_fallback_result(clean_input, outcome)

    # Temp file round-trip (design doc section 5 / 17: never persisted).
    payload = result.model_dump()
    path, payload = create_temp_json(payload)
    delete_temp_json(path)

    record_thought(outcome["ending_type"])

    return result
