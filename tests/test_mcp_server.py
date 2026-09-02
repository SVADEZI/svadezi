import asyncio
import json

import pytest

pytest.importorskip("mcp", reason="MCP server needs the optional 'mcp' extra")

from headroom.mcp_server import build_server  # noqa: E402


def _text(result):
    """Pull the text payload out of a tool result (mcp 1.x and 2.x shapes)."""
    content = getattr(result, "content", result)
    item = content[0]
    return item.text


@pytest.fixture(scope="module")
def server():
    # Guards the mcp 1.x FastMCP -> 2.x MCPServer rename: build_server() must
    # work against whichever major version is installed.
    return build_server()


def test_server_exposes_the_three_tools(server):
    tools = asyncio.run(server.list_tools())
    assert sorted(t.name for t in tools) == [
        "headroom_compress",
        "headroom_retrieve",
        "headroom_stats",
    ]


def test_compress_tool_reports_savings(server):
    payload = json.dumps([{"id": i, "user": f"u{i}", "role": "dev"} for i in range(30)])
    result = asyncio.run(server.call_tool("headroom_compress", {"content": payload}))
    body = json.loads(_text(result))
    assert body["kind"] == "json"
    assert body["stats"]["tokens_after"] < body["stats"]["tokens_before"]
    assert body["handle"].startswith("hr:")


def test_retrieve_tool_roundtrips_exactly(server):
    original = json.dumps([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    compressed = asyncio.run(
        server.call_tool("headroom_compress", {"content": original})
    )
    handle = json.loads(_text(compressed))["handle"]
    retrieved = asyncio.run(server.call_tool("headroom_retrieve", {"handle": handle}))
    assert json.loads(_text(retrieved))["content"] == original


def test_retrieve_tool_reports_unknown_handle(server):
    result = asyncio.run(
        server.call_tool("headroom_retrieve", {"handle": "hr:nosuchhandle"})
    )
    assert "error" in json.loads(_text(result))


def test_stats_tool_returns_totals(server):
    result = asyncio.run(server.call_tool("headroom_stats", {}))
    body = json.loads(_text(result))
    assert {"calls", "tokens_before", "tokens_after", "tokens_saved"} <= body.keys()
