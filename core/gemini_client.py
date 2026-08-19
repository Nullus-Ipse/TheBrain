"""
core/gemini_client.py

Talks to Google Gemini over plain REST (no SDK dependency — keeps the
app lightweight, per the design doc's deployment notes).

Gemini model chain:
    1. Gemini 3.5 Flash-Lite — primary
    2. Gemini 3.1 Flash-Lite — fallback

Responsibilities, and only these:
    - send the already-built prompt to Gemini
    - try the primary model, then the fallback model if necessary
    - ask for raw JSON back
    - translate transport/API failures into core.errors exceptions
    - return the raw text response

This module never decides what *kind* of result to generate — that's
core.prompt_selector's job. It also never validates the JSON shape —
that's core.json_validator's job.
"""

from __future__ import annotations

import requests

from core.config import (
    GEMINI_API_BASE,
    GEMINI_FALLBACK_MODEL,
    GEMINI_PRIMARY_MODEL,
    GEMINI_TIMEOUT,
    GOOGLE_API_KEY,
    MAX_OUTPUT_TOKENS,
    TEMPERATURE,
    get_setting,
)
from core.errors import (
    ConfigError,
    GeminiAPIError,
    GeminiQuotaError,
    GeminiSafetyBlockError,
    GeminiTimeoutError,
)


def _resolve_api_key() -> str:
    """Re-check secrets/env at call time (not just import time).

    Streamlit reruns the whole script on every interaction, so in
    practice `config.GOOGLE_API_KEY` is already fresh — but resolving
    again here means this function behaves correctly even if it's ever
    called from a long-lived process (tests, a worker, etc.) where the
    module was only imported once.
    """
    return get_setting("GOOGLE_API_KEY", GOOGLE_API_KEY) or ""


def _call_gemini(model: str, prompt: str) -> str:
    """Make a single request to a specific Gemini model.

    This function performs exactly one API call. Model selection and
    fallback logic are handled by generate_json_from_gemini().
    """
    api_key = _resolve_api_key()

    if not api_key:
        raise ConfigError("GOOGLE_API_KEY not configured.")

    url = f"{GEMINI_API_BASE}/models/{model}:generateContent"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": TEMPERATURE,
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "responseMimeType": "application/json",
        },
    }

    try:
        response = requests.post(
            url,
            params={"key": api_key},
            json=payload,
            timeout=GEMINI_TIMEOUT,
        )

    except requests.exceptions.Timeout as exc:
        raise GeminiTimeoutError(
            f"Gemini request timed out ({model})."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise GeminiAPIError(
            f"Gemini request failed ({model}): {exc}"
        ) from exc

    if response.status_code == 429:
        raise GeminiQuotaError(
            f"Gemini quota/rate limit exceeded ({model})."
        )

    if response.status_code == 403:
        raise ConfigError(
            f"Gemini rejected the API key ({model}, HTTP 403)."
        )

    if not response.ok:
        raise GeminiAPIError(
            f"Gemini returned HTTP {response.status_code} "
            f"({model}): {response.text[:300]}"
        )

    try:
        data = response.json()

    except ValueError as exc:
        raise GeminiAPIError(
            f"Gemini response was not valid JSON transport-side ({model})."
        ) from exc

    # ---------------------------------------------------------------
    # Safety handling
    # ---------------------------------------------------------------

    prompt_feedback = data.get("promptFeedback", {})

    if prompt_feedback.get("blockReason"):
        raise GeminiSafetyBlockError(
            f"Gemini blocked the prompt ({model}): "
            f"{prompt_feedback.get('blockReason')}"
        )

    candidates = data.get("candidates", [])

    if not candidates:
        raise GeminiAPIError(
            f"Gemini returned no candidates ({model})."
        )

    candidate = candidates[0]

    if candidate.get("finishReason") == "SAFETY":
        raise GeminiSafetyBlockError(
            f"Gemini blocked the response on safety grounds ({model})."
        )

    # ---------------------------------------------------------------
    # Extract response text
    # ---------------------------------------------------------------

    parts = candidate.get("content", {}).get("parts", [])

    text = "".join(
        part.get("text", "")
        for part in parts
    ).strip()

    if not text:
        raise GeminiAPIError(
            f"Gemini returned an empty response ({model})."
        )

    return text


def generate_json_from_gemini(prompt: str) -> str:
    """Generate JSON using the Gemini model fallback chain.

    Model order:

        Gemini 3.5 Flash-Lite
                ↓ failure
        Gemini 3.1 Flash-Lite
                ↓ failure
        raise the appropriate Gemini error

    The function returns the raw response text. JSON validation is
    intentionally handled elsewhere by core.json_validator.

    Raises:
        ConfigError:
            No API key configured or API key rejected.

        GeminiTimeoutError:
            Both model attempts timed out.

        GeminiQuotaError:
            Both model attempts were rejected due to quota/rate limits.

        GeminiSafetyBlockError:
            Gemini blocked the request/response.

        GeminiAPIError:
            Both model attempts failed for another API reason.
    """

    # ---------------------------------------------------------------
    # First attempt: Gemini 3.5 Flash-Lite
    # ---------------------------------------------------------------

    try:
        return _call_gemini(
            GEMINI_PRIMARY_MODEL,
            prompt,
        )

    except ConfigError:
        # A bad/missing API key isn't fixed by switching models.
        raise

    except GeminiSafetyBlockError:
        # Safety blocks are not necessarily model-specific.
        # Preserve the existing behavior rather than silently
        # bypassing a safety refusal with another model.
        raise

    except (
        GeminiTimeoutError,
        GeminiQuotaError,
        GeminiAPIError,
    ):
        # Primary failed. Continue to fallback.
        pass

    # ---------------------------------------------------------------
    # Second attempt: Gemini 3.1 Flash-Lite
    # ---------------------------------------------------------------

    try:
        return _call_gemini(
            GEMINI_FALLBACK_MODEL,
            prompt,
        )

    except ConfigError:
        raise

    except GeminiSafetyBlockError:
        raise

    except (
        GeminiTimeoutError,
        GeminiQuotaError,
        GeminiAPIError,
    ):
        # Both models failed.
        #
        # Raise a single useful error indicating that the entire
        # Gemini chain failed.
        raise GeminiAPIError(
            "Both Gemini models failed: "
            f"{GEMINI_PRIMARY_MODEL} and "
            f"{GEMINI_FALLBACK_MODEL}."
        )