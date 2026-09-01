"""probes/harness/adapters/__init__.py — the ADAPTERS registry, keyed by `wire_family`
(models.yaml's own field). The runner dispatches by wire family, never by vendor name
— one adapter module serves every vendor sharing that wire shape: all six remaining
OpenAI-compatible makers share `openai_compat`, and Gemini is the third and final
family, closing the registry at three keys for all 12 tracked models.
"""
from __future__ import annotations

from . import anthropic_messages, gemini, openai_compat

ADAPTERS = {
    "anthropic_messages": anthropic_messages,
    "openai_compat": openai_compat,
    "gemini": gemini,
}
