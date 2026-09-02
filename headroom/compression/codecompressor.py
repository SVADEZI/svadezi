"""CodeCompressor - AST-aware compression for source code.

When source files land in an LLM's context (RAG hits, repo dumps, stack-trace
neighbourhoods) the model usually needs the *shape* of the code -- imports,
class and function signatures, docstrings -- far more often than every line of
every body. CodeCompressor produces that skeleton.

* **Python** is parsed with the standard :mod:`ast` module. Function and method
  bodies are replaced with their docstring (if any) plus ``...``; module/class
  layout, decorators, signatures, and type annotations are preserved exactly via
  :func:`ast.unparse`.
* **Other languages** (JS, TS, Go, Rust, Java, C/C++) use a lexical fallback
  that strips comments and collapses blank lines/indentation runs. This is
  language-agnostic and safe, just less surgical than the Python path.

As with SmartCrusher, the full original is kept in the CCR cache so a model can
retrieve a specific body when the skeleton is not enough.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass

__all__ = ["CodeCompressor", "CodeResult"]

# Single-line comment markers for the lexical fallback, keyed by language.
_LINE_COMMENTS = {
    "javascript": "//",
    "typescript": "//",
    "js": "//",
    "ts": "//",
    "go": "//",
    "rust": "//",
    "java": "//",
    "c": "//",
    "cpp": "//",
    "c++": "//",
}
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


@dataclass
class CodeResult:
    text: str
    original: str
    language: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.text


class CodeCompressor:
    """Compress source code down to a structural skeleton."""

    def __init__(self, *, keep_docstrings: bool = True):
        self.keep_docstrings = keep_docstrings

    def compress(self, source: str, language: str = "python") -> CodeResult:
        language = (language or "python").lower()
        if language in ("python", "py"):
            text = self._compress_python(source)
        else:
            text = self._compress_lexical(source, language)
        return CodeResult(text=text, original=source, language=language)

    # -- python path --------------------------------------------------------

    def _compress_python(self, source: str) -> str:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # Not valid Python after all; fall back to the safe lexical path.
            return self._compress_lexical(source, "python")
        transformer = _BodyElider(self.keep_docstrings)
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        return ast.unparse(new_tree)

    # -- lexical fallback ---------------------------------------------------

    def _compress_lexical(self, source: str, language: str) -> str:
        text = _BLOCK_COMMENT.sub("", source)
        marker = _LINE_COMMENTS.get(language, "#")
        cleaned_lines = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(marker):
                continue
            # Drop trailing line comments only when clearly not inside a string.
            if marker in line and '"' not in line and "'" not in line:
                line = line.split(marker, 1)[0].rstrip()
                if not line.strip():
                    continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines)


class _BodyElider(ast.NodeTransformer):
    """Replace function/method bodies with ``[docstring +] ...``."""

    def __init__(self, keep_docstrings: bool):
        self.keep_docstrings = keep_docstrings

    def _elide(self, node):
        self.generic_visit(node)
        new_body: list[ast.stmt] = []
        if self.keep_docstrings:
            doc = ast.get_docstring(node, clean=False)
            if doc is not None:
                new_body.append(ast.Expr(value=ast.Constant(value=doc)))
        new_body.append(ast.Expr(value=ast.Constant(value=Ellipsis)))
        node.body = new_body
        return node

    visit_FunctionDef = _elide
    visit_AsyncFunctionDef = _elide

    def _strip_docstring(self, node):
        """Visit children, then optionally drop a leading docstring."""
        self.generic_visit(node)
        if not self.keep_docstrings and ast.get_docstring(node, clean=False) is not None:
            node.body = node.body[1:] or [ast.Expr(value=ast.Constant(value=Ellipsis))]
        return node

    visit_ClassDef = _strip_docstring
    visit_Module = _strip_docstring
