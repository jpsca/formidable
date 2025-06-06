"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


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
