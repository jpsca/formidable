"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_list_field():
    class TestForm(f.Form):
        tags = f.ListField()
        friends = f.ListField(type=int)
        wat = f.ListField()

    form = TestForm(
        {
            "tags[]": ["python", "formidable", "testing"],
            "friends[]": ["1", "2", "3"],
        }
    )

    assert form.tags.name == "tags[]"
    assert form.tags.value == ["python", "formidable", "testing"]

    assert form.friends.name == "friends[]"
    assert form.friends.value == [1, 2, 3]

    assert form.wat.name == "wat[]"
    assert form.wat.value == []

    data = form.save()
    print(data)
    assert data == {
        "tags": ["python", "formidable", "testing"],
        "friends": [1, 2, 3],
        "wat": [],
    }


def test_none_value():
    field = f.ListField()

    field.set(None)
    field.validate()
    assert field.value == []
    assert field.error is None


def test_empty_value():
    field = f.ListField()

    field.set([])
    field.validate()
    assert field.value == []
    assert field.error is None


def test_not_a_list_value():
    field = f.ListField()

    field.set("not a list")
    field.validate()
    assert field.error is None
    assert field.value == ["not a list"]


def test_invalid_list_type():
    field = f.ListField(type=int, strict=False)

    field.set(["no", "not an int", "nope"])
    field.validate()
    assert field.error is None
    assert field.value == []


def test_invalid_list_type_strict():
    field = f.ListField(type=int, strict=True)

    field.set(["no", "not an int", "nope"])
    field.validate()
    assert field.error == err.INVALID


def test_validate_min_items():
    field = f.ListField(min_items=3)

    field.set([1, 2])
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}

    field.set([1, 2, 3])
    field.validate()
    assert field.error is None


def test_invalid_min_items():
    with pytest.raises(ValueError):
        f.ListField(min_items="not an int")  # type: ignore


def test_validate_max_items():
    field = f.ListField(max_items=3)

    field.set([1, 2, 3, 4])
    field.validate()
    assert field.error == err.MAX_ITEMS
    assert field.error_args == {"max_items": 3}

    field.set([1, 2, 3])
    field.validate()
    assert field.error is None

    field.set([])
    field.validate()
    assert field.error is None


def test_invalid_max_items():
    with pytest.raises(ValueError):
        f.ListField(max_items="not an int")  # type: ignore


def test_validate_one_of():
    field = f.ListField(one_of=[1, 2, 3])

    field.set([1, 2])
    field.validate()
    assert field.error is None

    field.set([4])
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": [1, 2, 3]}

    field.set([])
    field.validate()
    assert field.error is None


def test_invalid_one_of():
    with pytest.raises(ValueError):
        f.ListField(one_of="not a list")  # type: ignore
