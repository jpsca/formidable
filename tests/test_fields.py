"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""
from uuid import uuid4

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


@pytest.mark.parametrize(
  "FieldType",
    [
        f.DateField,
        f.DateTimeField,
        f.EmailField,
        f.FloatField,
        f.IntegerField,
        f.SlugField,
        f.TextField,
        f.TimeField,
        f.URLField,
    ]
)
def test_value(FieldType):
    VALUE = uuid4().hex

    field = FieldType()
    field.set(VALUE, "whatever")
    assert field.value == VALUE

    field = FieldType()
    field.set("", VALUE)
    assert field.value == ""

    field = FieldType()
    field.set(None, VALUE)
    assert field.value == VALUE


def test_is_multiple():
    """
    Test that the `multiple` property works correctly.
    """
    field = f.TextField()
    assert not field.multiple

    field = f.ListField()
    assert field.multiple
