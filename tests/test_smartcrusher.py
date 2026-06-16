import json

from headroom.compression import SmartCrusher


def test_tabularizes_array_of_dicts():
    data = [
        {"id": 1, "name": "alpha", "role": "admin"},
        {"id": 2, "name": "beta", "role": "user"},
        {"id": 3, "name": "gamma", "role": "user"},
    ]
    result = SmartCrusher().crush(data)
    out = json.loads(result.text)
    assert out["_cols"] == ["id", "name", "role"]
    assert out["_rows"][0] == [1, "alpha", "admin"]
    # Keys appear once in the header rather than once per row.
    assert len(result.text) < len(result.original)


def test_heterogeneous_rows_fill_with_null():
    data = [{"a": 1, "b": 2}, {"a": 3}]
    out = json.loads(SmartCrusher().crush(data).text)
    assert out["_cols"] == ["a", "b"]
    assert out["_rows"][1] == [3, None]


def test_drops_empty_fields():
    data = {"keep": "yes", "empty": "", "none": None, "list": [], "obj": {}}
    out = json.loads(SmartCrusher().crush(data).text)
    assert out == {"keep": "yes"}


def test_keeps_empty_fields_when_disabled():
    data = {"keep": "yes", "none": None}
    out = json.loads(SmartCrusher(drop_empty=False).crush(data).text)
    assert out == {"keep": "yes", "none": None}


def test_truncates_long_strings():
    data = {"blob": "x" * 1000}
    out = json.loads(SmartCrusher(max_string=100).crush(data).text)
    assert len(out["blob"]) < 1000
    assert "chars]" in out["blob"]


def test_accepts_json_string_input():
    result = SmartCrusher().crush('[{"a":1,"b":2},{"a":3,"b":4}]')
    assert "_cols" in result.text


def test_looks_like_json():
    assert SmartCrusher.looks_like_json('{"a": 1}')
    assert SmartCrusher.looks_like_json("[1, 2, 3]")
    assert not SmartCrusher.looks_like_json("def f(): pass")
    assert not SmartCrusher.looks_like_json("")
