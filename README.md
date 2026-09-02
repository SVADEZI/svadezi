# Headroom

**Context compression for LLM agents — fewer tokens, same answers.**

Tool outputs, logs, RAG chunks, and source files balloon an agent's context
window. Headroom compresses that bulk *before* it reaches the model — typically
**60–95% fewer tokens** — while keeping the information the model actually needs.
Anything dropped is kept in a local, content-addressed cache so the agent can
retrieve the full original on demand.

> A clean-room reimplementation of the core ideas from
> [chopratejas/headroom](https://github.com/chopratejas/headroom): the
> SmartCrusher and CodeCompressor algorithms, an MCP server, and an
> OpenAI-compatible compression proxy.

## Install

```bash
pip install -e .           # core library + proxy (stdlib only)
pip install -e ".[mcp]"    # add the MCP server
pip install -e ".[dev]"    # add pytest
```

## Library

```python
from headroom import compress, retrieve, get_stats

result = compress(tool_output)     # auto-detects JSON / code / text
send_to_llm(result.text)           # denser payload

original = retrieve(result.handle) # full content back when a detail is needed
get_stats()                        # cumulative tokens saved
```

`compress` returns a `CompressionResult` with `.text`, `.handle`, `.kind`,
`.tokens_before`, `.tokens_after`, `.saved_tokens`, and `.ratio`.

## What's included

### SmartCrusher — JSON tool outputs
Structure-aware compression for the JSON agents see most: arrays of records,
nested objects, mixed types. It tabularizes homogeneous arrays (keys emitted
once, not per row), drops empty fields, and truncates oversized strings — output
stays valid JSON.

```python
from headroom import SmartCrusher
SmartCrusher().crush([{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]).text
# -> {"_cols":["id","name"],"_rows":[[1,"a"],[2,"b"]]}
```

### CodeCompressor — source files
AST-aware skeletonization. Python is parsed with the `ast` module: function and
method bodies become `...` (docstrings optionally kept) while imports, classes,
decorators, signatures, and annotations are preserved exactly. Other languages
(JS, TS, Go, Rust, Java, C/C++) use a lexical fallback that strips comments and
blank lines.

```python
from headroom import CodeCompressor
CodeCompressor().compress(source, "python").text
```

### MCP server
Exposes compression to any MCP client (e.g. Claude Code) via three tools:
`headroom_compress`, `headroom_retrieve`, `headroom_stats`. Works with both
mcp 1.x (`FastMCP`) and mcp 2.x (`MCPServer`).

```bash
pip install -e ".[mcp]"
headroom mcp
```

This repo ships a `.mcp.json` that registers the server for Claude Code. It
points at `${CLAUDE_PROJECT_DIR}/.venv/bin/headroom` — an absolute path rather
than a bare `headroom`, because MCP servers are spawned at session start and
cannot rely on the SessionStart hook having already put the venv on `PATH`. If
you install headroom globally instead, `"command": "headroom"` is enough.

### Proxy server
A drop-in proxy for any OpenAI-compatible API. Point your client's base URL at
it and large message content is compressed locally before being forwarded
upstream — no code changes.

```bash
headroom proxy --port 8787 --upstream https://api.openai.com
export OPENAI_BASE_URL=http://localhost:8787/v1
# GET http://localhost:8787/headroom/stats for live savings
```

## CLI

```bash
headroom compress data.json --stats     # compress a file (or stdin)
headroom proxy --port 8787              # run the proxy
headroom mcp                            # run the MCP server
headroom stats                          # cumulative session stats
```

## Reversible by design (CCR)

Every `compress` call (unless `reversible=False`) stashes the original under
`~/.headroom/cache` (override with `HEADROOM_CACHE_DIR`) keyed by content hash,
and returns a short `hr:…` handle. `retrieve(handle)` returns the exact original.
Nothing leaves the machine.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
