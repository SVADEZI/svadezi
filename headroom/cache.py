"""Content-cache for reversible compression (CCR).

When Headroom compresses a payload it keeps the *original* content in a local,
content-addressed cache and hands back a short handle. An agent that later
discovers it needs a detail the compression dropped can call ``retrieve(handle)``
to get the full original back. Nothing leaves the machine: the cache lives under
``~/.headroom/cache`` by default (override with ``HEADROOM_CACHE_DIR``).
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from pathlib import Path

__all__ = ["ContentCache", "default_cache"]

HANDLE_PREFIX = "hr:"


def _default_dir() -> Path:
    env = os.environ.get("HEADROOM_CACHE_DIR")
    if env:
        return Path(env)
    return Path.home() / ".headroom" / "cache"


class ContentCache:
    """A content-addressed store mapping handles to original payloads.

    Entries are keyed by the SHA-256 of the content, so storing the same payload
    twice is free and de-duplicates automatically. An in-memory layer fronts the
    on-disk store; pass ``persist=False`` for an ephemeral (test) cache.
    """

    def __init__(self, directory: Path | str | None = None, *, persist: bool = True):
        self.persist = persist
        self.directory = Path(directory) if directory is not None else _default_dir()
        self._mem: dict[str, str] = {}
        self._lock = threading.Lock()
        if self.persist:
            self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, digest: str) -> Path:
        return self.directory / f"{digest}.json"

    def store(self, content: str) -> str:
        """Cache ``content`` and return its handle (``hr:<digest>``)."""
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
        handle = f"{HANDLE_PREFIX}{digest}"
        with self._lock:
            if handle in self._mem:
                return handle
            self._mem[handle] = content
            if self.persist:
                self._path(digest).write_text(
                    json.dumps({"handle": handle, "content": content}),
                    encoding="utf-8",
                )
        return handle

    def retrieve(self, handle: str) -> str | None:
        """Return the original content for ``handle``, or ``None`` if unknown."""
        if not handle.startswith(HANDLE_PREFIX):
            handle = f"{HANDLE_PREFIX}{handle}"
        with self._lock:
            if handle in self._mem:
                return self._mem[handle]
            if self.persist:
                path = self._path(handle[len(HANDLE_PREFIX):])
                if path.exists():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    self._mem[handle] = data["content"]
                    return data["content"]
        return None

    def clear(self) -> None:
        with self._lock:
            self._mem.clear()
            if self.persist and self.directory.exists():
                for path in self.directory.glob("*.json"):
                    path.unlink()


# Process-wide default cache used by the top-level ``compress``/``retrieve`` API.
default_cache = ContentCache()
