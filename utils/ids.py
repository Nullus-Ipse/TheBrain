"""
utils/ids.py

Short random identifiers — used for things like the temp thought
JSON filenames (`thought_<id>.json`). Not cryptographic, not a
primary key, just short and collision-unlikely enough for a
per-session temp file name.
"""

from __future__ import annotations

import uuid


def generate_id(length: int = 12) -> str:
    """A short lowercase hex id, e.g. 'a3f9c1d0284b'.

    `length` is clamped to [1, 32] (uuid4 hex is 32 chars long).
    """
    length = max(1, min(32, length))
    return uuid.uuid4().hex[:length]


def generate_prefixed_id(prefix: str, length: int = 12) -> str:
    """e.g. generate_prefixed_id('thought') -> 'thought_a3f9c1d0284b'."""
    return f"{prefix}_{generate_id(length)}"
