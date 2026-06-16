"""Headroom MCP server.

Exposes compression to any MCP-capable agent (Claude Code, etc.) as three tools:

* ``headroom_compress``  - compress a payload, returns the dense text + a handle.
* ``headroom_retrieve``  - fetch the original content for a handle.
* ``headroom_stats``     - report cumulative token savings for the session.

The MCP SDK is an optional dependency. Install with ``pip install headroom-ai[mcp]``
(or ``pip install mcp``) and run ``headroom mcp`` / ``python -m headroom.mcp_server``.
"""

from __future__ import annotations

import json

from . import compress as _compress
from . import get_stats as _get_stats
from . import retrieve as _retrieve

__all__ = ["build_server", "main"]


def build_server():
    """Construct and return the FastMCP server instance.

    Imported lazily so the rest of Headroom works without the ``mcp`` package.
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:  # pragma: no cover - depends on optional dep
        raise SystemExit(
            "The MCP server needs the 'mcp' package. "
            "Install it with:  pip install headroom-ai[mcp]"
        ) from exc

    server = FastMCP("headroom")

    @server.tool()
    def headroom_compress(
        content: str, kind: str = "auto", language: str = ""
    ) -> str:
        """Compress text/JSON/code before it enters the model context.

        Returns JSON with the compressed ``text``, a ``handle`` for retrieval,
        and per-call token ``stats``.
        """
        result = _compress(content, kind=kind, language=language or None)
        return json.dumps(
            {
                "text": result.text,
                "handle": result.handle,
                "kind": result.kind,
                "stats": {
                    "tokens_before": result.tokens_before,
                    "tokens_after": result.tokens_after,
                    "tokens_saved": result.saved_tokens,
                    "ratio": round(result.ratio, 4),
                },
            }
        )

    @server.tool()
    def headroom_retrieve(handle: str) -> str:
        """Return the full original content for a compression handle."""
        original = _retrieve(handle)
        if original is None:
            return json.dumps({"error": f"unknown handle: {handle}"})
        return json.dumps({"handle": handle, "content": original})

    @server.tool()
    def headroom_stats() -> str:
        """Report cumulative compression statistics for this session."""
        return json.dumps(_get_stats())

    return server


def main() -> None:
    build_server().run()


if __name__ == "__main__":  # pragma: no cover
    main()
