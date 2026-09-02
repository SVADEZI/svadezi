"""Headroom proxy - drop-in compression for OpenAI-compatible APIs.

Point any OpenAI-compatible client (OpenAI SDK, LiteLLM, LangChain, curl, a
coding agent...) at this proxy instead of the provider, and Headroom compresses
bulky message content locally before forwarding the request upstream. No code
changes in the client beyond the base URL.

    headroom proxy --port 8787 --upstream https://api.openai.com

    export OPENAI_BASE_URL=http://localhost:8787/v1
    # ...run your app as usual...

Only message ``content`` that is large enough to be worth compressing is
touched; short instructions pass through untouched so prompts aren't mangled.
Built on the standard library so it has no runtime dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock

from .pipeline import compress, get_stats

__all__ = ["run", "compress_payload"]

DEFAULT_UPSTREAM = "https://api.openai.com"
# Hop-by-hop headers that must not be forwarded (RFC 7230 §6.1).
_HOP_BY_HOP = {
    "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
    "te", "trailers", "transfer-encoding", "upgrade", "content-length", "host",
}


def compress_payload(payload: dict, *, min_chars: int = 600) -> dict:
    """Return a copy of an OpenAI chat ``payload`` with large content crushed.

    Each message's ``content`` is compressed only when it exceeds ``min_chars``,
    so short system/user prompts are left exactly as-is.
    """
    messages = payload.get("messages")
    if not isinstance(messages, list):
        return payload

    new_messages = []
    for message in messages:
        if not isinstance(message, dict):
            new_messages.append(message)
            continue
        content = message.get("content")
        if isinstance(content, str) and len(content) >= min_chars:
            message = {**message, "content": compress(content, reversible=False).text}
        new_messages.append(message)
    return {**payload, "messages": new_messages}


class _Handler(BaseHTTPRequestHandler):
    upstream = DEFAULT_UPSTREAM
    min_chars = 600
    server_version = "Headroom/0.1"

    def log_message(self, fmt, *args):  # quieter default logging
        pass

    def do_GET(self):
        if self.path.rstrip("/") == "/headroom/stats":
            self._send_json(200, get_stats())
            return
        self._forward(body=None)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        body = raw
        # Compress chat-completions request bodies; pass everything else through.
        if "/chat/completions" in self.path and raw:
            try:
                payload = json.loads(raw)
                body = json.dumps(compress_payload(payload, min_chars=self.min_chars)).encode()
            except (ValueError, TypeError):
                body = raw
        self._forward(body=body)

    # -- helpers ------------------------------------------------------------

    def _forward(self, body: bytes | None):
        url = self.upstream.rstrip("/") + self.path
        headers = {
            k: v for k, v in self.headers.items() if k.lower() not in _HOP_BY_HOP
        }
        req = urllib.request.Request(url, data=body, headers=headers, method=self.command)
        try:
            with urllib.request.urlopen(req) as resp:
                self._relay(resp.status, resp.headers, resp.read())
        except urllib.error.HTTPError as err:
            self._relay(err.code, err.headers, err.read())
        except urllib.error.URLError as err:
            self._send_json(502, {"error": f"upstream unreachable: {err.reason}"})

    def _relay(self, status, headers, payload: bytes):
        self.send_response(status)
        for key, value in headers.items():
            if key.lower() not in _HOP_BY_HOP:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_json(self, status: int, obj: dict):
        payload = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def run(
    host: str = "127.0.0.1",
    port: int = 8787,
    upstream: str | None = None,
    min_chars: int = 600,
) -> None:
    """Start the proxy server (blocking)."""
    _Handler.upstream = upstream or os.environ.get("HEADROOM_UPSTREAM", DEFAULT_UPSTREAM)
    _Handler.min_chars = min_chars
    httpd = ThreadingHTTPServer((host, port), _Handler)
    print(f"headroom proxy listening on http://{host}:{port} -> {_Handler.upstream}")
    print(f"  point your client at  http://{host}:{port}/v1")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover
        httpd.shutdown()


def _main(argv=None) -> None:  # pragma: no cover - CLI glue
    parser = argparse.ArgumentParser(description="Headroom compression proxy")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--upstream", default=None)
    parser.add_argument("--min-chars", type=int, default=600)
    args = parser.parse_args(argv)
    run(args.host, args.port, args.upstream, args.min_chars)


if __name__ == "__main__":  # pragma: no cover
    _main()
