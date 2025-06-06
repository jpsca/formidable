"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_validate_min_length():
    field = f.TextField(min_length=5)

    field.set("1234")
    field.validate()
    assert field.error == err.MIN_LENGTH
    assert field.error_args == {"min_length": 5}

    field.set("12345")
    field.validate()
    assert field.error is None


def test_invalid_min_length():
    with pytest.raises(ValueError):
        f.TextField(min_length="not an int")  # type: ignore


def test_validate_max_length():
    field = f.TextField(max_length=5)

    field.set("123456")
    field.validate()
    assert field.error == err.MAX_LENGTH
    assert field.error_args == {"max_length": 5}

    field.set("12345")
    field.validate()
    assert field.error is None

    field.set("")
    field.validate()
    assert field.error is None


def test_invalid_max_length():
    with pytest.raises(ValueError):
        f.TextField(max_length="not an int")  # type: ignore


def test_validate_pattern():
    field = f.TextField(pattern=r"^\d{3}-\d{2}-\d{4}$")

    field.set("123-45-6789")
    field.validate()
    assert field.error is None

    field.set("123456789")
    field.validate()
    assert field.error == err.PATTERN
    assert field.error_args == {"pattern": r"^\d{3}-\d{2}-\d{4}$"}

    field.set("12-345-6789")
    field.validate()
    assert field.error == err.PATTERN
    assert field.error_args == {"pattern": r"^\d{3}-\d{2}-\d{4}$"}


def test_invalid_pattern():
    with pytest.raises(ValueError):
        f.TextField(pattern=33)  # type: ignore
