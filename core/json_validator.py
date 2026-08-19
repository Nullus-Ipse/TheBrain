"""
core/json_validator.py

Turns Gemini's raw text response into a validated ThoughtResult, or
raises InvalidJSONError so thought_engine can fall back gracefully.

Handles the two things LLMs reliably do wrong even when told not to:
    - wrapping JSON in ```json ... ``` code fences
    - adding a "Sure! Here's your JSON:" preamble/postamble
"""

from __future__ import annotations

import json
import re

from pydantic import ValidationError

from core.errors import InvalidJSONError
from core.models import ThoughtResult

_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _strip_code_fences(text: str) -> str:
    match = _CODE_FENCE_RE.search(text)
    if match:
        return match.group(1).strip()
    return text.strip()


def _extract_json_object(text: str) -> str:
    """Grab the outermost {...} span, in case there's stray prose around it."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def _clamp_relevance(parsed: dict) -> dict:
    for item in parsed.get("thought_chain", []):
        if isinstance(item, dict) and "relevance" in item:
            try:
                item["relevance"] = max(0, min(100, float(item["relevance"])))
            except (TypeError, ValueError):
                pass
    return parsed


def parse_gemini_response(raw_text: str) -> dict:
    """Best-effort recovery of a JSON object from raw model text.

    Raises InvalidJSONError if nothing parseable can be found.
    """
    cleaned = _strip_code_fences(raw_text)
    cleaned = _extract_json_object(cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise InvalidJSONError(f"Could not parse JSON: {exc}") from exc

    if not isinstance(parsed, dict):
        raise InvalidJSONError("Top-level JSON value was not an object.")

    return parsed


def validate_thought_json(raw_text: str, expected_ending_type: str | None = None) -> ThoughtResult:
    """Parse + validate raw Gemini text into a ThoughtResult.

    If `expected_ending_type` is given, the ending.type in the response
    must match it exactly — this enforces the "Python decides the fate"
    rule at the data layer, not just the prompt layer.

    Raises InvalidJSONError on any failure (bad JSON, schema mismatch,
    or ending-type mismatch) so the caller can fall back uniformly.
    """
    parsed = parse_gemini_response(raw_text)
    parsed = _clamp_relevance(parsed)

    try:
        result = ThoughtResult.model_validate(parsed)
    except ValidationError as exc:
        raise InvalidJSONError(f"Schema validation failed: {exc}") from exc

    if expected_ending_type and result.ending.type != expected_ending_type:
        raise InvalidJSONError(
            f"Ending type mismatch: expected {expected_ending_type!r}, "
            f"got {result.ending.type!r}"
        )

    return result
