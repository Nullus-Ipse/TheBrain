"""
content/loading_messages.py

Flavor text for the fake neural-processing sequence (design doc
section 10). It should never just say "Loading..." — it should look
like an overengineered diagnostic dump for a machine that is about to
fail at its one job.

Two pools:
    CANONICAL_SEQUENCE — the doc's own ordered example. Good default
        if you want a consistent, deterministic-feeling sequence.
    EXTRA_MESSAGES — additional lines for variety, meant to be
        shuffled in so repeat visitors don't see the exact same script
        every time.

get_processing_sequence() builds a randomized run for actual use.
"""

from __future__ import annotations

import random

CANONICAL_SEQUENCE: list[str] = [
    "INITIALIZING COGNITIVE ENGINE...",
    "Establishing required synapses...",
    "Recruiting {neuron_count} neurons...",
    "Allocating working memory...",
    "Searching long-term memory...",
    "Long-term memory returned {irrelevant_memory_count} irrelevant memories.",
    "Suppressing irrelevant memories...",
    "Suppression unsuccessful.",
    "Establishing semantic associations...",
    "Calculating associative distance...",
    "Cross-referencing memories...",
    "Activating secondary thought pathways...",
    "Secondary thought pathway has become the primary thought pathway.",
    "Attempting to recover original thought...",
    "Original thought integrity: {integrity}%.",
    "Continuing analysis...",
]

EXTRA_MESSAGES: list[str] = [
    "Initializing frontal cortex...",
    "Rebooting frontal cortex...",
    "Frontal cortex reports it is 'basically fine'.",
    "Querying hippocampus...",
    "Hippocampus is not responding.",
    "Retrying hippocampus...",
    "Bypassing hippocampus.",
    "Loading semantic network...",
    "Semantic network partially corrupted.",
    "Ignoring corruption and proceeding anyway...",
    "Cross-checking against prior thoughts...",
    "No prior thoughts of comparable quality found.",
    "Compressing working memory...",
    "Working memory compression achieved 4%.",
    "Discarding unnecessary context...",
    "All context has been discarded.",
    "Re-acquiring context...",
    "Context re-acquisition failed. Continuing without it.",
    "Measuring cognitive drift...",
    "Cognitive drift exceeds recommended threshold.",
    "Recommended threshold was arbitrary. Proceeding.",
    "Consulting internal logic circuits...",
    "Internal logic circuits decline to comment.",
    "Stabilizing thought vector...",
    "Thought vector refuses to stabilize.",
]


def get_processing_sequence(extra_count: int = 4) -> list[str]:
    """Build one run of loading messages: the canonical sequence with a
    few EXTRA_MESSAGES lines shuffled in, so no two THINK presses read
    identically.

    Callers should `.format(...)` the templated lines (the ones with
    `{neuron_count}` etc.) using values from core.fake_metrics — this
    module only supplies the text, not the numbers.
    """
    extras = random.sample(EXTRA_MESSAGES, k=min(extra_count, len(EXTRA_MESSAGES)))
    sequence = list(CANONICAL_SEQUENCE)

    # Splice extras in at random (non-edge) positions so they read as
    # interruptions rather than a tacked-on tail.
    for line in extras:
        insert_at = random.randint(2, max(2, len(sequence) - 2))
        sequence.insert(insert_at, line)

    return sequence
