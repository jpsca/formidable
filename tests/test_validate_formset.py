"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


class ChildForm(f.Form):
    meh = f.TextField(required=False)


def test_validate_min_items():
    field = f.FormSet(ChildForm, min_items=3)

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
    })
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
    })
    field.validate()
    assert field.error is None


def test_validate_mixed_min_items():
    field = f.FormSet(ChildForm, min_items=3)

    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
        ]
    )
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}

    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
        ],
    )
    field.validate()
    assert field.error is None

    field.set(
        {
            "1": {"meh": "1"},  # update object
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
        ],
    )
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}


def test_invalid_min_items():
    with pytest.raises(ValueError):
        f.FormSet(ChildForm, min_items="not an int")  # type: ignore


def test_validate_max_items():
    field = f.FormSet(ChildForm, max_items=3)

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
        "3": {"meh": "4"},
    })
    field.validate()
    assert field.error == err.MAX_ITEMS
    assert field.error_args == {"max_items": 3}

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
    })
    field.validate()
    assert field.error is None

    field.set({})
    field.validate()
    assert field.error is None


def test_validate_mixed_max_items():
    field = f.FormSet(ChildForm, max_items=3)

    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error == err.MAX_ITEMS
    assert field.error_args == {"max_items": 3}

    field.set(
        {
            "1": {"meh": "1"},  # update object
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error is None

    field.set(
        {},
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error is None

    field.set({})
    field.validate()
    assert field.error is None


def test_invalid_max_items():
    with pytest.raises(ValueError):
        f.FormSet(ChildForm, max_items="not an int")  # type: ignore
