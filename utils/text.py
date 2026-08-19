"""
utils/text.py

Small string helpers for cleaning up and sampling user input / model
output. Nothing here knows what a "thought" is — just plain text
manipulation.
"""

from __future__ import annotations


def safe_strip(text: str | None) -> str:
    """None-safe .strip() — returns '' for None instead of raising."""
    return (text or "").strip()


def first_word(text: str, *, default: str = "thought") -> str:
    """The first whitespace-delimited word of `text`, lowercased.
    Falls back to `default` for empty/whitespace-only input."""
    words = safe_strip(text).split()
    return words[0].lower() if words else default


def truncate(text: str, max_length: int, *, suffix: str = "…") -> str:
    """Shorten `text` to at most `max_length` characters (suffix
    included), without cutting mid-word where avoidable."""
    text = safe_strip(text)
    if len(text) <= max_length:
        return text
    cut = text[: max_length - len(suffix)]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut + suffix
