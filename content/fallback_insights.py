"""
content/fallback_insights.py

Static insight lines, used ONLY as an emergency fallback by
core.fallback — when Google API fails, JSON is invalid, a safety block
fires, or the quota is exceeded (design doc / revised plan: "normally,
the AI should generate the insight... fallback is only used when...").

core.fallback imports FALLBACK_INSIGHTS from here automatically when
this file exists; that name is load-bearing. Keep every entry
confident-sounding, harmless, and useless — never real advice.
"""

from __future__ import annotations

FALLBACK_INSIGHTS: list[str] = [
    "A door is just a wall that got promoted.",
    "If you close your eyes, the room becomes shy.",
    "Every spoon is a tiny shovel for soup.",
    "Silence is just volume that gave up.",
    "A shadow is a reflection that took the day off.",
    "Stairs are just a ladder that stopped trying.",
    "A mirror is a wall with a very good memory.",
    "An umbrella is a roof for people who move too much.",
    "A calendar is just time, filed alphabetically by mistake.",
    "Every hallway is a room that couldn't decide what to be.",
    "A clock is a circle that got tired of going nowhere.",
    "Socks are gloves that gave up on ambition.",
    "A window is a wall that learned to be honest.",
    "Every echo is a sound asking to be believed twice.",
    "A pillow is a promise your head makes to itself.",
]
