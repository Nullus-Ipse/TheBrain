"""
core/models.py

Pydantic models for the thought-chain JSON contract. These are the
source of truth for what Gemini is allowed to hand back — used by
core/json_validator.py to validate (and lightly repair) responses.

Schema mirrors the design doc (section 8) plus the richer optional
`insight` object from the revised plan.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

EndingType = Literal[
    "thought_lost",
    "cognitive_drift",
    "cognitive_loop",
    "useless_insight",
    "unexpectedly_useful",
]


class AnalysisMetrics(BaseModel):
    neuron_count: int = Field(ge=0)
    synaptic_load: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    cognitive_stability: float = Field(ge=0, le=100)


class ThoughtChainItem(BaseModel):
    thought: str = Field(min_length=1, max_length=80)
    relevance: float = Field(ge=0, le=100)

    @field_validator("thought")
    @classmethod
    def _strip(cls, v: str) -> str:
        return v.strip()


class Insight(BaseModel):
    text: str = Field(min_length=1, max_length=400)
    confidence: float = Field(default=90.0, ge=0, le=100)
    practical_usefulness: float = Field(default=0.5, ge=0, le=100)
    scientific_validity: str = Field(default="Pending")


class Ending(BaseModel):
    type: EndingType
    message: str = Field(min_length=1, max_length=200)
    insight: Optional[Insight] = None


class ThoughtResult(BaseModel):
    """The full validated shape the UI renders from."""

    input: str
    analysis: AnalysisMetrics
    thought_chain: list[ThoughtChainItem] = Field(min_length=3, max_length=15)
    ending: Ending

    # Not part of Gemini's output — stamped on by thought_engine so the
    # UI always knows whether it's looking at real or fallback content.
    used_fallback: bool = False

    @field_validator("thought_chain")
    @classmethod
    def _relevance_should_trend_down(
        cls, items: list[ThoughtChainItem]
    ) -> list[ThoughtChainItem]:
        # Soft check only — we don't reject the whole response over minor
        # non-monotonicity (a little jitter is fine, even funnier), but a
        # chain that goes UP overall is almost certainly a broken response.
        if len(items) >= 2 and items[-1].relevance > items[0].relevance:
            raise ValueError(
                "thought_chain relevance must trend downward "
                "(first item should be more relevant than the last)"
            )
        return items
