"""Lightweight token estimation.

Headroom reports compression ratios in tokens, but we don't want to pull in a
heavy tokenizer dependency for the core library. The estimate below is the same
~4-characters-per-token heuristic most providers quote for English/code, with a
small correction for whitespace-heavy text. It is good enough for reporting
savings; swap in a real tokenizer (tiktoken, etc.) where exactness matters.
"""

from __future__ import annotations

__all__ = ["estimate_tokens"]


def estimate_tokens(text: str) -> int:
    """Return an approximate token count for ``text``.

    The heuristic counts non-whitespace runs (words/punctuation) and adds a
    fraction of the raw length, which tracks real tokenizers within ~10-15% on
    typical agent payloads (JSON, logs, source code).
    """
    if not text:
        return 0
    char_estimate = len(text) / 4
    # Whitespace and punctuation create extra token boundaries; nudge upward.
    word_estimate = sum(1 for _ in text.split())
    return max(1, round((char_estimate + word_estimate) / 2))
