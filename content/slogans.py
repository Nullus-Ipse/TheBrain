"""
content/slogans.py

Rotating footer text (design doc section 14). Confident, pseudo-
scientific, clearly a joke.
"""

from __future__ import annotations

import random

SLOGANS: list[str] = [
    "Made after the real thing. 💡",
    "Powered by absolutely no neuroscience.",
    "Clinically questionable. Technically functional.",
    "Peer reviewed by nobody.",
    "Your brain probably does this too.",
    "Crafted after thorough analysis of a real brain.",
    "97% synthetic. 3% regret.",
    "Not a medical device. Not a device at all, really.",
    "Endorsed by zero neurologists.",
    "Thinking, simulated. Results not included.",
]


def get_random_slogan() -> str:
    return random.choice(SLOGANS)
