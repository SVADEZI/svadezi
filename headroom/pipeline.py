"""The Headroom pipeline: detect content type, compress, account for savings.

This is the front door most callers use::

    from headroom import compress, retrieve, get_stats

    result = compress(tool_output)        # auto-detects JSON vs code vs text
    model_input = result.text             # denser payload to send to the LLM
    original = retrieve(result.handle)    # full content back when needed
    get_stats()                           # cumulative tokens saved
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any, Literal

from .cache import ContentCache, default_cache
from .compression import CodeCompressor, SmartCrusher
from .tokenizer import estimate_tokens

__all__ = ["compress", "retrieve", "get_stats", "reset_stats", "CompressionResult"]

Kind = Literal["auto", "json", "code", "text"]

# Common source-code extensions/aliases -> CodeCompressor language hint.
_CODE_LANGUAGES = {
    "python", "py", "javascript", "js", "typescript", "ts",
    "go", "rust", "rs", "java", "c", "cpp", "c++",
}


@dataclass
class CompressionResult:
    """The result of a single ``compress`` call."""

    text: str
    handle: str | None
    kind: str
    tokens_before: int
    tokens_after: int

    @property
    def saved_tokens(self) -> int:
        return self.tokens_before - self.tokens_after

    @property
    def ratio(self) -> float:
        """Fraction of tokens removed (0.0 - 1.0)."""
        if self.tokens_before == 0:
            return 0.0
        return self.saved_tokens / self.tokens_before

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.text


@dataclass
class _Stats:
    calls: int = 0
    tokens_before: int = 0
    tokens_after: int = 0
    by_kind: dict[str, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        saved = self.tokens_before - self.tokens_after
        ratio = saved / self.tokens_before if self.tokens_before else 0.0
        return {
            "calls": self.calls,
            "tokens_before": self.tokens_before,
            "tokens_after": self.tokens_after,
            "tokens_saved": saved,
            "ratio": round(ratio, 4),
            "by_kind": dict(self.by_kind),
        }


_stats = _Stats()
_stats_lock = Lock()


def _detect_kind(content: str, language: str | None) -> Kind:
    if language and language.lower() in _CODE_LANGUAGES:
        return "code"
    if SmartCrusher.looks_like_json(content):
        return "json"
    # Heuristic: code tends to contain these tokens far more than prose.
    code_signals = ("def ", "class ", "function ", "import ", "fn ", "=>", "{")
    if sum(sig in content for sig in code_signals) >= 2:
        return "code"
    return "text"


def compress(
    content: Any,
    *,
    kind: Kind = "auto",
    language: str | None = None,
    reversible: bool = True,
    cache: ContentCache | None = None,
) -> CompressionResult:
    """Compress ``content`` for cheaper delivery to an LLM.

    ``content`` may be a string or any JSON-serialisable object. ``kind`` forces
    a strategy; the default ``"auto"`` detects JSON vs code vs plain text. When
    ``reversible`` is true the original is stored in the CCR cache and the
    returned handle can be passed to :func:`retrieve`.
    """
    cache = cache or default_cache

    if isinstance(content, (dict, list)):
        text_in = __import__("json").dumps(content, ensure_ascii=False)
        resolved = "json" if kind == "auto" else kind
    else:
        text_in = str(content)
        resolved = _detect_kind(text_in, language) if kind == "auto" else kind

    if resolved == "json":
        text_out = SmartCrusher().crush(content).text
    elif resolved == "code":
        text_out = CodeCompressor().compress(text_in, language or "python").text
    else:
        text_out = text_in  # plain text: nothing structural to exploit

    handle = cache.store(text_in) if reversible else None

    tokens_before = estimate_tokens(text_in)
    tokens_after = estimate_tokens(text_out)
    _record(resolved, tokens_before, tokens_after)

    return CompressionResult(
        text=text_out,
        handle=handle,
        kind=resolved,
        tokens_before=tokens_before,
        tokens_after=tokens_after,
    )


def retrieve(handle: str, *, cache: ContentCache | None = None) -> str | None:
    """Return the original content previously stored under ``handle``."""
    cache = cache or default_cache
    return cache.retrieve(handle)


def get_stats() -> dict[str, Any]:
    """Return cumulative compression statistics for this process."""
    with _stats_lock:
        return _stats.as_dict()


def reset_stats() -> None:
    with _stats_lock:
        _stats.calls = 0
        _stats.tokens_before = 0
        _stats.tokens_after = 0
        _stats.by_kind = {}


def _record(kind: str, before: int, after: int) -> None:
    with _stats_lock:
        _stats.calls += 1
        _stats.tokens_before += before
        _stats.tokens_after += after
        _stats.by_kind[kind] = _stats.by_kind.get(kind, 0) + (before - after)
