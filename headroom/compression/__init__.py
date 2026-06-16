"""Compression algorithms used by Headroom."""

from .codecompressor import CodeCompressor, CodeResult
from .smartcrusher import CrushResult, SmartCrusher

__all__ = ["SmartCrusher", "CrushResult", "CodeCompressor", "CodeResult"]
