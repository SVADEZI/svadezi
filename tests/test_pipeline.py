import json

import pytest

from headroom import compress, get_stats, reset_stats, retrieve
from headroom.cache import ContentCache
from headroom.proxy import compress_payload


@pytest.fixture(autouse=True)
def _clean_stats():
    reset_stats()
    yield
    reset_stats()


def test_compress_autodetects_json():
    data = [{"id": i, "name": f"n{i}"} for i in range(5)]
    result = compress(data)
    assert result.kind == "json"
    assert "_cols" in result.text


def test_compress_autodetects_code():
    src = "def f(x):\n    return x + 1\n\nclass A:\n    def m(self):\n        return 1\n"
    result = compress(src)
    assert result.kind == "code"
    assert "return x + 1" not in result.text


def test_reversible_retrieve_roundtrip():
    cache = ContentCache(persist=False)
    original = '[{"a":1,"b":2},{"a":3,"b":4}]'
    result = compress(original, cache=cache)
    assert result.handle is not None
    assert retrieve(result.handle, cache=cache) == original


def test_retrieve_unknown_handle_returns_none():
    cache = ContentCache(persist=False)
    assert retrieve("hr:doesnotexist", cache=cache) is None


def test_stats_accumulate():
    compress([{"id": i, "v": i * 2} for i in range(10)])
    stats = get_stats()
    assert stats["calls"] == 1
    assert stats["tokens_saved"] >= 0
    assert "json" in stats["by_kind"]


def test_result_ratio_and_saved():
    result = compress([{"id": i, "name": f"name{i}"} for i in range(20)])
    assert result.saved_tokens == result.tokens_before - result.tokens_after
    assert 0.0 <= result.ratio <= 1.0


def test_proxy_compress_payload_only_touches_large_content():
    big = json.dumps([{"id": i, "name": f"n{i}", "role": "user"} for i in range(50)])
    payload = {
        "model": "gpt-x",
        "messages": [
            {"role": "system", "content": "be brief"},
            {"role": "user", "content": big},
        ],
    }
    out = compress_payload(payload, min_chars=600)
    assert out["messages"][0]["content"] == "be brief"  # short -> untouched
    assert len(out["messages"][1]["content"]) < len(big)  # large -> compressed
    assert out["model"] == "gpt-x"
