"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_json_field_default_dict():
    field = f.JSONField(default={"lorem": "ipsum"})
    assert field.default == {"lorem": "ipsum"}


def test_json_field_default_str():
    field = f.JSONField(default='{"lorem": "ipsum"}')
    assert field.default == {"lorem": "ipsum"}


def test_json_field_default_invalid():
    with pytest.raises(ValueError):
        f.JSONField(default="not a json")


def test_json_field():
    class TestForm(f.Form):
        json = f.JSONField()
        default_json = f.JSONField(default={"lorem": "ipsum"})

    form = TestForm({"json": {"hello": "world"}})

    assert form.is_valid
    print(form.get_errors())
    assert form.json.value == {"hello": "world"}
    assert form.default_json.value == {"lorem": "ipsum"}

    data = form.save()
    print(data)
    assert data == {
        "json": {"hello": "world"},
        "default_json": {"lorem": "ipsum"},
    }


@pytest.mark.parametrize(
    "data, expected",
    [
        ['{"lorem": "ipsum"}', {"lorem": "ipsum"}],
        # spaces around json
        [' {"lorem":  "ipsum"} ', {"lorem": "ipsum"}],
        # empty string should be None
        ["", None],
        # None should be None
        [None, None],
        # dict should be accepted as is
        [{"lorem": "ipsum"}, {"lorem": "ipsum"}],
        # empty dict should be accepted as is
        [{}, {}],
        # empty string with spaces should be None
        ["   ", None],
    ],
)
def test_valid_jsons(data, expected):
    field = f.JSONField(required=False)
    field.set(data)

    assert field.error is None
    assert field.value == expected


def test_json_field_invalid():
    class TestForm(f.Form):
        json = f.JSONField(required=False)

    form = TestForm({"json": ["not a json"]})
    assert form.is_invalid
    assert form.json.error == err.INVALID_JSON


def test_json_field_render():
    field = f.JSONField(required=False)
    field.id = "meh"

    field.set({"hello": "world"})
    html = str(field.textarea())
    expected = '<textarea id="meh" name="">{&#34;hello&#34;: &#34;world&#34;}</textarea>'
    assert html == expected

    field.set(None)
    html = str(field.textarea())
    expected = '<textarea id="meh" name=""></textarea>'
    assert html == expected
