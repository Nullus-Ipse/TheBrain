"""
content/ai_examples.py

Few-shot JSON examples shown to Gemini inside the prompt, so it
matches the expected schema and comedic tone instead of just guessing.
These are NOT shown to the user as a result — they're purely there to
guide generation (design doc: "These examples should not be shown
directly to the user as the final result unless you want them as
fallback").

core.prompts imports TRASH_EXAMPLE and INSIGHT_EXAMPLE from here
automatically when this file exists; those two names are load-bearing
and shouldn't be renamed. The extra per-ending examples below aren't
wired into core/ yet — they're here so prompts.py can be extended
later (e.g. a dedicated example per trash ending) without redesigning
this file.
"""

from __future__ import annotations

TRASH_EXAMPLE = """{
  "input": "Should I buy a new car?",
  "analysis": {
    "neuron_count": 36739784,
    "synaptic_load": 82.4,
    "memory_usage": 64.2,
    "cognitive_stability": 31.8
  },
  "thought_chain": [
    {"thought": "car", "relevance": 100},
    {"thought": "vehicle", "relevance": 91},
    {"thought": "road", "relevance": 77},
    {"thought": "traffic", "relevance": 61},
    {"thought": "red light", "relevance": 38},
    {"thought": "apple", "relevance": 16},
    {"thought": "banana", "relevance": 6}
  ],
  "ending": {
    "type": "thought_lost",
    "message": "Original thought no longer available."
  }
}"""

INSIGHT_EXAMPLE = """{
  "input": "What should I have for dinner?",
  "analysis": {
    "neuron_count": 29182456,
    "synaptic_load": 77.1,
    "memory_usage": 58.9,
    "cognitive_stability": 22.4
  },
  "thought_chain": [
    {"thought": "dinner", "relevance": 100},
    {"thought": "food", "relevance": 92},
    {"thought": "plate", "relevance": 79},
    {"thought": "circle", "relevance": 63},
    {"thought": "moon", "relevance": 41},
    {"thought": "cheese", "relevance": 22},
    {"thought": "mouse", "relevance": 9}
  ],
  "ending": {
    "type": "useless_insight",
    "message": "GENUINE INSIGHT DETECTED",
    "insight": {
      "text": "The moon is only a snack because no one has tried to eat it seriously enough.",
      "confidence": 91.4,
      "practical_usefulness": 0.2,
      "scientific_validity": "Pending"
    }
  }
}"""

COGNITIVE_DRIFT_EXAMPLE = """{
  "input": "What should I do with my fish tank?",
  "analysis": {
    "neuron_count": 41872319,
    "synaptic_load": 74.8,
    "memory_usage": 66.3,
    "cognitive_stability": 28.9
  },
  "thought_chain": [
    {"thought": "fish tank", "relevance": 100},
    {"thought": "water", "relevance": 90},
    {"thought": "ocean", "relevance": 78},
    {"thought": "waves", "relevance": 64},
    {"thought": "surfing", "relevance": 45},
    {"thought": "falling down", "relevance": 27},
    {"thought": "gravity documentaries", "relevance": 9}
  ],
  "ending": {
    "type": "cognitive_drift",
    "message": "Cognitive drift: 91.0%. Current thought: gravity documentaries."
  }
}"""

COGNITIVE_LOOP_EXAMPLE = """{
  "input": "Should I repaint my kitchen?",
  "analysis": {
    "neuron_count": 33221190,
    "synaptic_load": 69.5,
    "memory_usage": 55.0,
    "cognitive_stability": 40.2
  },
  "thought_chain": [
    {"thought": "kitchen", "relevance": 100},
    {"thought": "paint", "relevance": 88},
    {"thought": "color", "relevance": 73},
    {"thought": "walls", "relevance": 58},
    {"thought": "house", "relevance": 44},
    {"thought": "kitchen", "relevance": 30}
  ],
  "ending": {
    "type": "cognitive_loop",
    "message": "Cognitive loop detected. Thought has returned to its starting point."
  }
}"""

UNEXPECTEDLY_USEFUL_EXAMPLE = """{
  "input": "Why do I feel so tired lately?",
  "analysis": {
    "neuron_count": 25011983,
    "synaptic_load": 60.1,
    "memory_usage": 48.4,
    "cognitive_stability": 71.0
  },
  "thought_chain": [
    {"thought": "tired", "relevance": 100},
    {"thought": "sleep", "relevance": 85},
    {"thought": "water", "relevance": 70},
    {"thought": "hydration", "relevance": 55},
    {"thought": "drinking water", "relevance": 40}
  ],
  "ending": {
    "type": "unexpectedly_useful",
    "message": "ERROR: thought became unexpectedly useful.",
    "insight": {
      "text": "Drink some water.",
      "confidence": 65.0,
      "practical_usefulness": 72.0,
      "scientific_validity": "Pending"
    }
  }
}"""
