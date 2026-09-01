"""probes/harness/adapters/__init__.py — the ADAPTERS registry, keyed by `wire_family`
(models.yaml's own field). The runner dispatches by wire family, never by vendor name
— one adapter module serves every vendor sharing that wire shape (all six remaining
OpenAI-compatible vendors will share `openai_compat` once plan 09-02 adds it).
"""
from __future__ import annotations

from . import anthropic_messages

ADAPTERS = {
    "anthropic_messages": anthropic_messages,
}
