"""
core/ — the "director" layer of Brain Simulator.

Nothing in this package decides whether the audience laughs.
It decides whether the brain loses the thought, drifts, loops,
or (rarely) stumbles into a fake insight — and it hands the writing
job to Gemini.

    Python  = director  (this package)
    Gemini  = writer     (core.gemini_client)
    UI      = actor      (ui/, not part of this package)
"""

__version__ = "0.1.0"
