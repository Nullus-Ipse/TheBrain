"""
core/temp_file.py

Creates and deletes the per-session temporary JSON file described in
the design doc (section 5 / "Temporary JSON on a Hosted App"):

    Generate JSON -> validate -> write temp file -> load into
    session_state -> delete file -> render from session_state.

Some hosting environments restrict filesystem writes. If writing
fails, this degrades gracefully to an in-memory object instead of
raising — the joke still works, no permanent storage is ever used
either way.
"""

from __future__ import annotations

import json
import os
import uuid

from core.config import TEMP_DIR


def _temp_path(thought_id: str) -> str:
    return os.path.join(TEMP_DIR, f"thought_{thought_id}.json")


def create_temp_json(data: dict) -> tuple[str | None, dict]:
    """Write `data` to a temp JSON file.

    Returns (path, data). `path` is None if the write failed or the
    filesystem is unavailable — callers should treat that as "use the
    in-memory `data` instead," not as an error.
    """
    thought_id = uuid.uuid4().hex[:12]
    path = _temp_path(thought_id)

    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return path, data
    except OSError:
        # Read-only filesystem, permissions issue, etc. — degrade gracefully.
        return None, data


def load_temp_json(path: str | None, fallback_data: dict) -> dict:
    """Read the temp file back if it exists, else return fallback_data unchanged."""
    if not path:
        return fallback_data
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except OSError:
        return fallback_data


def delete_temp_json(path: str | None) -> None:
    """Best-effort delete. Never raises — a failed cleanup shouldn't break the UI."""
    if not path:
        return
    try:
        os.remove(path)
    except OSError:
        pass
