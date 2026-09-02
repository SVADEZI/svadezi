"""SmartCrusher - structure-aware compression for JSON tool outputs.

Tool outputs that reach an LLM are usually JSON: arrays of records, deeply
nested objects, mixed types, and lots of repeated keys and null fields. Feeding
them verbatim wastes tokens. SmartCrusher rewrites the structure into an
equivalent-but-denser form *without losing information that matters*:

* **Tabularizes** arrays of homogeneous objects: keys are emitted once as a
  header instead of being repeated on every row.
* **Drops empty fields** (``null``, ``""``, ``[]``, ``{}``) which rarely carry
  signal for the model. Disable with ``drop_empty=False``.
* **Truncates** very long strings to a head/tail window with an elision marker.
* **Minifies** the result (no incidental whitespace).

The transform is intentionally readable: the output is still valid JSON the
model can parse. True round-tripping is provided by the CCR cache (see
``headroom.cache``), so SmartCrusher can be aggressive here.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

__all__ = ["SmartCrusher", "CrushResult"]

_EMPTY = (None, "", [], {})


@dataclass
class CrushResult:
    """Outcome of crushing a JSON payload."""

    text: str
    original: str
    transformed: Any

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.text


class SmartCrusher:
    """Compress JSON-shaped data into a denser, equivalent representation."""

    def __init__(
        self,
        *,
        drop_empty: bool = True,
        max_string: int = 280,
        min_rows_for_table: int = 2,
        min_shared_keys: int = 2,
    ):
        self.drop_empty = drop_empty
        self.max_string = max_string
        self.min_rows_for_table = min_rows_for_table
        self.min_shared_keys = min_shared_keys

    # -- public API ---------------------------------------------------------

    def crush(self, data: Any) -> CrushResult:
        """Crush ``data`` (a JSON string or already-parsed object)."""
        if isinstance(data, (str, bytes)):
            original = data.decode("utf-8") if isinstance(data, bytes) else data
            parsed = json.loads(original)
        else:
            parsed = data
            original = json.dumps(parsed, ensure_ascii=False)
        transformed = self._transform(parsed)
        text = json.dumps(transformed, ensure_ascii=False, separators=(",", ":"))
        return CrushResult(text=text, original=original, transformed=transformed)

    @staticmethod
    def looks_like_json(text: str) -> bool:
        stripped = text.strip()
        if not stripped or stripped[0] not in "[{":
            return False
        try:
            json.loads(stripped)
        except (ValueError, TypeError):
            return False
        return True

    # -- transforms ---------------------------------------------------------

    def _transform(self, value: Any) -> Any:
        if isinstance(value, dict):
            return self._transform_dict(value)
        if isinstance(value, list):
            return self._transform_list(value)
        if isinstance(value, str):
            return self._truncate(value)
        return value

    def _transform_dict(self, obj: dict) -> dict:
        out: dict[str, Any] = {}
        for key, val in obj.items():
            tval = self._transform(val)
            if self.drop_empty and tval in _EMPTY:
                continue
            out[key] = tval
        return out

    def _transform_list(self, items: list) -> Any:
        transformed = [self._transform(item) for item in items]
        table = self._tabularize(items)
        if table is not None:
            return table
        return transformed

    def _tabularize(self, items: list) -> dict | None:
        """Fold an array of homogeneous dicts into a columnar table.

        Returns a ``{"_cols": [...], "_rows": [[...]]}`` structure when it is a
        net win (enough rows sharing enough keys), else ``None``.
        """
        if len(items) < self.min_rows_for_table:
            return None
        if not all(isinstance(item, dict) for item in items):
            return None

        # Use the union of keys, ordered by first appearance, so heterogeneous
        # records still tabularize with ``null`` filling the gaps.
        cols: list[str] = []
        seen: set[str] = set()
        for item in items:
            for key in item:
                if key not in seen:
                    seen.add(key)
                    cols.append(key)
        if len(cols) < self.min_shared_keys:
            return None

        rows = []
        for item in items:
            row = []
            for col in cols:
                cell = item.get(col)
                row.append(self._transform(cell) if col in item else None)
            rows.append(row)
        return {"_cols": cols, "_rows": rows}

    def _truncate(self, text: str) -> str:
        if len(text) <= self.max_string:
            return text
        head = self.max_string * 2 // 3
        tail = self.max_string - head
        omitted = len(text) - head - tail
        return f"{text[:head]}…[+{omitted} chars]…{text[-tail:]}"
