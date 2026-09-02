"""Headroom - context compression for LLM agents.

Compress tool outputs, logs, files, and RAG chunks before they reach the model:
fewer tokens, same answers, with reversible retrieval when a detail is needed.

Public API::

    from headroom import compress, retrieve, get_stats
    from headroom import SmartCrusher, CodeCompressor
"""

from __future__ import annotations

from .cache import ContentCache, default_cache
from .compression import CodeCompressor, CodeResult, CrushResult, SmartCrusher
from .pipeline import (
    CompressionResult,
    compress,
    get_stats,
    reset_stats,
    retrieve,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "compress",
    "retrieve",
    "get_stats",
    "reset_stats",
    "CompressionResult",
    "SmartCrusher",
    "CrushResult",
    "CodeCompressor",
    "CodeResult",
    "ContentCache",
    "default_cache",
]
