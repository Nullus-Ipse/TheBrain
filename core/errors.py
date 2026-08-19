"""
core/errors.py

Every way this app can fail, named, plus the in-universe copy for it.

The rule from the design doc: errors should be transformed into part of
the experience wherever possible. So each exception here carries an
`error_code` that `ui/` (or anything else) can look up in
ERROR_MESSAGES to get a comedic title + body instead of a stack trace.

None of these exceptions should ever be shown raw to a user.
"""

from __future__ import annotations

import random

try:  # pragma: no cover - optional content/ package
    from content.failure_messages import FAILURE_MESSAGES as _CONTENT_FAILURE_MESSAGES
except ImportError:
    _CONTENT_FAILURE_MESSAGES = None


class BrainSimulatorError(Exception):
    """Base class for every deliberately-handled failure in this app."""

    error_code: str = "cognitive_failure"

    def __init__(self, message: str = "", *, error_code: str | None = None):
        super().__init__(message or self.error_code)
        if error_code:
            self.error_code = error_code


class ConfigError(BrainSimulatorError):
    """Required configuration (usually the API key) is missing."""

    error_code = "neural_key_missing"


class InputTooShortError(BrainSimulatorError):
    error_code = "no_thought_detected"


class InputTooLongError(BrainSimulatorError):
    error_code = "working_memory_overflow"


class GeminiTimeoutError(BrainSimulatorError):
    error_code = "synaptic_timeout"


class GeminiQuotaError(BrainSimulatorError):
    error_code = "cognitive_capacity_exceeded"


class GeminiSafetyBlockError(BrainSimulatorError):
    error_code = "cognitive_protection_protocol"


class GeminiAPIError(BrainSimulatorError):
    """Catch-all for non-2xx / connection-level failures from Gemini."""

    error_code = "neural_connection_failure"


class InvalidJSONError(BrainSimulatorError):
    """Gemini responded, but the JSON was missing, malformed, or didn't
    match the schema / requested ending type."""

    error_code = "cognitive_structure_corrupted"


# ---------------------------------------------------------------------------
# In-universe copy, keyed by error_code. `ui/` renders these instead of the
# real exception message.
#
# content/failure_messages.py, when present, supplies several {"title",
# "body"} variants per error_code and get_error_copy() picks one at
# random. The dict below is only the built-in fallback used when that
# file doesn't exist — one fixed variant per code, so the app never has
# a code with no copy at all.
# ---------------------------------------------------------------------------
ERROR_MESSAGES: dict[str, dict[str, str]] = {
    "neural_key_missing": {
        "title": "NEURAL KEY MISSING",
        "body": "The brain cannot legally contact itself.",
    },
    "no_thought_detected": {
        "title": "NO THOUGHT DETECTED",
        "body": "Please provide a thought.",
    },
    "working_memory_overflow": {
        "title": "WORKING MEMORY OVERFLOW",
        "body": "Please think about something smaller.",
    },
    "synaptic_timeout": {
        "title": "SYNAPTIC TIMEOUT",
        "body": "The neurons took too long and are now pretending to be busy.",
    },
    "cognitive_capacity_exceeded": {
        "title": "COGNITIVE CAPACITY EXCEEDED",
        "body": "Too many brains are currently thinking.",
    },
    "cognitive_protection_protocol": {
        "title": "COGNITIVE PROTECTION PROTOCOL",
        "body": "The thought was too spicy for the fake brain.",
    },
    "neural_connection_failure": {
        "title": "NEURAL CONNECTION FAILURE",
        "body": "The brain cannot currently contact its secondary cognitive substrate.",
    },
    "cognitive_structure_corrupted": {
        "title": "COGNITIVE STRUCTURE CORRUPTED",
        "body": "Thought could not be reconstructed.",
    },
    "cognitive_failure": {
        "title": "COGNITIVE FAILURE",
        "body": "The brain has stopped cooperating.",
    },
}


def get_error_copy(error_code: str) -> dict[str, str]:
    """Look up display copy for an error_code, with a safe generic fallback.

    Prefers a random variant from content.failure_messages.FAILURE_MESSAGES
    when that file is available; otherwise uses the single built-in
    ERROR_MESSAGES entry for the code (or the generic "cognitive_failure"
    entry if the code itself is unrecognized).
    """
    if _CONTENT_FAILURE_MESSAGES and error_code in _CONTENT_FAILURE_MESSAGES:
        return random.choice(_CONTENT_FAILURE_MESSAGES[error_code])
    if _CONTENT_FAILURE_MESSAGES and "cognitive_failure" in _CONTENT_FAILURE_MESSAGES:
        return random.choice(_CONTENT_FAILURE_MESSAGES["cognitive_failure"])
    return ERROR_MESSAGES.get(error_code, ERROR_MESSAGES["cognitive_failure"])
