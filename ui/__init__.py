"""
ui/ — the "actor" layer of Brain Simulator.

Nothing in this package decides what happens (that's core/) or what
gets said (that's content/ + Gemini). It only performs: it takes a
ThoughtResult (or an error code) and puts on a show.

    Python  = director  (core/)
    Gemini  = writer     (core.gemini_client)
    UI      = actor      (this package)

Entry point: ui.page.render_page(). Everything else in here is a
building block that render_page() assembles, but each module also
works standalone if you want to reuse a panel elsewhere.
"""

__version__ = "0.1.0"
