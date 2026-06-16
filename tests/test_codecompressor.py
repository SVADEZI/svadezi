import ast

from headroom.compression import CodeCompressor

PY_SOURCE = '''
import os


class Greeter:
    """A greeter."""

    def __init__(self, name: str) -> None:
        """Store the name."""
        self.name = name
        self.calls = 0

    def greet(self) -> str:
        self.calls += 1
        return f"hello {self.name}"


def top_level(x, y=2):
    z = x + y
    return z * 2
'''


def test_python_skeleton_elides_bodies_keeps_signatures():
    out = CodeCompressor().compress(PY_SOURCE, "python").text
    # Output is still valid Python.
    ast.parse(out)
    # Signatures and structure survive.
    assert "class Greeter" in out
    assert "def greet(self) -> str" in out
    assert "def top_level(x, y=2)" in out
    assert "import os" in out
    # Bodies are gone.
    assert "self.calls += 1" not in out
    assert "z = x + y" not in out
    # It is shorter than the original.
    assert len(out) < len(PY_SOURCE)


def test_python_keeps_docstrings_by_default():
    out = CodeCompressor().compress(PY_SOURCE, "python").text
    assert "A greeter." in out
    assert "Store the name." in out


def test_python_can_drop_docstrings():
    out = CodeCompressor(keep_docstrings=False).compress(PY_SOURCE, "python").text
    assert "A greeter." not in out


def test_invalid_python_falls_back_to_lexical():
    src = "def broken(:\n  # comment\n  x = 1\n"
    out = CodeCompressor().compress(src, "python").text
    assert "# comment" not in out


def test_lexical_strips_comments_for_other_languages():
    js = """
// a line comment
function add(a, b) {
  /* block
     comment */
  return a + b; // trailing
}
"""
    out = CodeCompressor().compress(js, "javascript").text
    assert "line comment" not in out
    assert "block" not in out
    assert "function add(a, b)" in out
    assert "return a + b;" in out
