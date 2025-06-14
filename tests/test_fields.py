"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""
import pytest

import formidable as f
from formidable import errors as err


@pytest.mark.parametrize(
  "FieldType",
    [
        f.DateField,
        f.DateTimeField,
        f.EmailField,
        f.FloatField,
        f.IntegerField,
        f.SlugField,
        f.TimeField,
        f.URLField,
    ]
)
def test_required(FieldType):
    field = FieldType()
    field.set(None)
    field.validate()
    assert field.error == err.REQUIRED
    assert field.error_message == err.MESSAGES[err.REQUIRED]

    field = FieldType()
    field.set("")
    field.validate()
    assert field.error == err.REQUIRED

    field = FieldType(required=False)
    field.set(None)
    field.validate()
    assert field.error is None
    assert field.error_message == ""


@pytest.mark.parametrize(
  "FieldType,value",
    [
        (f.DateField, "not a date"),
        (f.DateTimeField, "not a datetime"),
        (f.IntegerField, "not an int"),
        (f.FloatField, "not a float"),
        (f.TimeField, "not a time"),
    ]
)
def test_invalid(FieldType, value):
    field = FieldType()
    field.set(value)
    field.validate()
    assert field.error == err.INVALID
    assert field.error_message == err.MESSAGES[err.INVALID]


@pytest.mark.parametrize(
  "FieldType,objvalue",
    [
        (f.DateField, "2025-05-05"),
        (f.DateTimeField, "2025-05-05T00:00:00"),
        (f.EmailField, "test@example.com"),
        (f.FloatField, "5.0"),
        (f.IntegerField, "5"),
        (f.SlugField, "test"),
        (f.TimeField, "12 PM"),
        (f.URLField, "http://test.com"),
    ]
)
def test_reqdata_over_objvalue(FieldType, objvalue):
    field = FieldType(required=False)
    field.set("", objvalue)
    assert field.value == ""


def test_before_hook():
    """
    Test that the before hook is called before setting the value.
    """
    def before_hook(value):
        return value + " (from before)"

    field = f.TextField(before=[before_hook])
    field.set("Hello")
    assert field.value == "Hello (from before)"


def test_before_hook_error():
    """
    Test that ValueError raised in before hook is handled correctly.
    """
    def before_hook(value):
        raise ValueError("Error in before hook", {"foo": "bar"})

    field = f.TextField(before=[before_hook])
    field.set("Hello")
    assert field.error == "Error in before hook"
    assert field.error_args == {"foo": "bar"}


def test_after_hook():
    """
    Test that the after hook is called after setting the value.
    """
    def after_hook(value):
        return value + " (from after)"

    field = f.TextField(after=[after_hook])
    field.set("Hello")
    field.validate()
    assert field.value == "Hello (from after)"


def test_after_hook_error():
    """
    Test that ValueError raised in after hook is handled correctly.
    """
    def after_hook(value):
        raise ValueError("Error in after hook", {"foo": "bar"})

    field = f.TextField(after=[after_hook])
    field.set("Hello")
    field.validate()
    assert field.error == "Error in after hook"
    assert field.error_args == {"foo": "bar"}


def test_is_multiple():
    """
    Test that the `multiple` property works correctly.
    """
    field = f.TextField()
    assert not field.multiple

    field = f.ListField()
    assert field.multiple
