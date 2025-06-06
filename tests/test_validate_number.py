"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_validate_gt(FieldType):
    field = FieldType(gt=10)

    field.set(10)
    field.validate()
    assert field.error == err.GT
    assert field.error_args == {"gt": 10}

    field.set(15)
    field.validate()
    assert field.error is None


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_gt(FieldType):
    with pytest.raises(ValueError):
        FieldType(gt="not a number")


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_validate_gte(FieldType):
    field = FieldType(gte=10)

    field.set(5)
    field.validate()
    assert field.error == err.GTE
    assert field.error_args == {"gte": 10}

    field.set(10)
    field.validate()
    assert field.error is None


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_gte(FieldType):
    with pytest.raises(ValueError):
        FieldType(gte="not a number")


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_validate_lt(FieldType):
    field = FieldType(lt=10)

    field.set(10)
    field.validate()
    assert field.error == err.LT
    assert field.error_args == {"lt": 10}

    field.set(5)
    field.validate()
    assert field.error is None


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_lt(FieldType):
    with pytest.raises(ValueError):
        FieldType(lt="not a number")


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_validate_lte(FieldType):
    field = FieldType(lte=10)

    field.set(15)
    field.validate()
    assert field.error == err.LTE
    assert field.error_args == {"lte": 10}

    field.set(10)
    field.validate()
    assert field.error is None


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_lte(FieldType):
    with pytest.raises(ValueError):
        FieldType(lte="not a number")


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_validate_multiple_of(FieldType):
    field = FieldType(multiple_of=5)

    field.set(4)
    field.validate()
    assert field.error == err.MULTIPLE_OF
    assert field.error_args == {"multiple_of": 5}

    field.set(5)
    field.validate()
    assert field.error is None

    field.set(10)
    field.validate()
    assert field.error is None


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_multiple_of(FieldType):
    with pytest.raises(ValueError):
        FieldType(multiple_of="not a number")
