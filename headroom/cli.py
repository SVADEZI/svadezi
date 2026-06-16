"""Command-line entry point for Headroom.

    headroom compress [FILE] [--kind auto|json|code|text] [--language py]
    headroom proxy [--port 8787] [--upstream URL]
    headroom mcp
    headroom stats
"""

from __future__ import annotations

import argparse
import json
import sys

from . import compress, get_stats


def _cmd_compress(args) -> int:
    data = open(args.file).read() if args.file else sys.stdin.read()
    result = compress(data, kind=args.kind, language=args.language)
    if args.stats:
        info = {
            "handle": result.handle,
            "kind": result.kind,
            "tokens_before": result.tokens_before,
            "tokens_after": result.tokens_after,
            "tokens_saved": result.saved_tokens,
            "ratio": round(result.ratio, 4),
        }
        print(json.dumps(info, indent=2), file=sys.stderr)
    print(result.text)
    return 0


def _cmd_proxy(args) -> int:
    from .proxy import run

    run(args.host, args.port, args.upstream, args.min_chars)
    return 0


def _cmd_mcp(_args) -> int:
    from .mcp_server import main

    main()
    return 0


def _cmd_stats(_args) -> int:
    print(json.dumps(get_stats(), indent=2))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="headroom", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_compress = sub.add_parser("compress", help="compress a file or stdin")
    p_compress.add_argument("file", nargs="?", help="input file (default: stdin)")
    p_compress.add_argument(
        "--kind", default="auto", choices=["auto", "json", "code", "text"]
    )
    p_compress.add_argument("--language", default=None, help="language hint for code")
    p_compress.add_argument(
        "--stats", action="store_true", help="print token stats to stderr"
    )
    p_compress.set_defaults(func=_cmd_compress)

    p_proxy = sub.add_parser("proxy", help="run the compression proxy")
    p_proxy.add_argument("--host", default="127.0.0.1")
    p_proxy.add_argument("--port", type=int, default=8787)
    p_proxy.add_argument("--upstream", default=None)
    p_proxy.add_argument("--min-chars", type=int, default=600)
    p_proxy.set_defaults(func=_cmd_proxy)

    p_mcp = sub.add_parser("mcp", help="run the MCP server")
    p_mcp.set_defaults(func=_cmd_mcp)

    p_stats = sub.add_parser("stats", help="print cumulative stats")
    p_stats.set_defaults(func=_cmd_stats)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
