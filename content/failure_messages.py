"""
content/failure_messages.py

The comedic title + body for every error_code raised in core/errors.py
(design doc section 16: "Errors should be transformed into part of the
experience wherever possible").

core.errors.get_error_copy() prefers this file automatically when it's
present — nothing else needs to change to pick these up. Each
error_code maps to a LIST of {"title", "body"} variants; a random one
is chosen so repeat failures don't read identically. Keep at least one
entry per code that core/errors.py defines, or that code falls back to
its own built-in default.
"""

from __future__ import annotations

FAILURE_MESSAGES: dict[str, list[dict[str, str]]] = {
    "neural_key_missing": [
        {
            "title": "NEURAL KEY MISSING",
            "body": "The brain cannot legally contact itself.",
        },
        {
            "title": "NEURAL KEY MISSING",
            "body": "No credentials on file. The brain has been reported to itself.",
        },
    ],
    "no_thought_detected": [
        {
            "title": "NO THOUGHT DETECTED",
            "body": "Please provide a thought.",
        },
        {
            "title": "NO THOUGHT DETECTED",
            "body": "The input field is emptier than most conversations at 3am.",
        },
    ],
    "working_memory_overflow": [
        {
            "title": "WORKING MEMORY OVERFLOW",
            "body": "Please think about something smaller.",
        },
        {
            "title": "WORKING MEMORY OVERFLOW",
            "body": "That thought does not fit. Please downsize your curiosity.",
        },
    ],
    "synaptic_timeout": [
        {
            "title": "SYNAPTIC TIMEOUT",
            "body": "The neurons took too long and are now pretending to be busy.",
        },
        {
            "title": "SYNAPTIC TIMEOUT",
            "body": "Synapse response exceeded patience threshold. Try again.",
        },
    ],
    "cognitive_capacity_exceeded": [
        {
            "title": "COGNITIVE CAPACITY EXCEEDED",
            "body": "Too many brains are currently thinking.",
        },
        {
            "title": "COGNITIVE CAPACITY EXCEEDED",
            "body": "Global thought queue is full. Please wait your turn to be confused.",
        },
    ],
    "cognitive_protection_protocol": [
        {
            "title": "COGNITIVE PROTECTION PROTOCOL",
            "body": "The thought was too spicy for the fake brain.",
        },
        {
            "title": "COGNITIVE PROTECTION PROTOCOL",
            "body": "That thought has been quarantined for everyone's safety, mostly the brain's.",
        },
    ],
    "neural_connection_failure": [
        {
            "title": "NEURAL CONNECTION FAILURE",
            "body": "The brain cannot currently contact its secondary cognitive substrate.",
        },
        {
            "title": "NEURAL CONNECTION FAILURE",
            "body": "Signal lost between synthetic frontal lobe and the internet.",
        },
    ],
    "cognitive_structure_corrupted": [
        {
            "title": "COGNITIVE STRUCTURE CORRUPTED",
            "body": "Thought could not be reconstructed.",
        },
        {
            "title": "COGNITIVE STRUCTURE CORRUPTED",
            "body": "The thought arrived in pieces. None of the pieces matched.",
        },
    ],
    "cognitive_failure": [
        {
            "title": "COGNITIVE FAILURE",
            "body": "The brain has stopped cooperating.",
        },
        {
            "title": "COGNITIVE FAILURE",
            "body": "Something went wrong. The brain declines to elaborate.",
        },
    ],
}
