"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_integer_field():
    class TestForm(f.Form):
        age = f.IntegerField()
        min_age = f.IntegerField(default=18)

    form = TestForm({"age": ["20"]})

    assert form.age.name == "age"
    assert form.age.value == 20
    assert form.min_age.value == 18

    data = form.save()
    print(data)
    assert data == {
        "age": 20,
        "min_age": 18,
    }


def test_float_field():
    class TestForm(f.Form):
        x = f.FloatField()
        y = f.FloatField()
        z = f.FloatField(default=0)

    form = TestForm(
        {
            "x": ["20"],
            "y": ["15.5"],
        }
    )

    assert form.x.name == "x"
    assert form.x.value == 20.0
    assert form.y.value == 15.5
    assert form.z.value == 0.0

    data = form.save()
    print(data)
    assert data == {
        "x": 20.0,
        "y": 15.5,
        "z": 0.0,
    }


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


def test_validate_one_of_integer():
    one_of = [1, 2, 3, 4]
    field = f.IntegerField(one_of=one_of)

    field.set(2)
    field.validate()
    assert field.error is None

    field.set(5)
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": one_of}


def test_validate_one_of_float():
    one_of = [1.0, 2.0, 3.5, 4.0]
    field = f.FloatField(one_of=one_of)

    field.set(2)
    field.validate()
    assert field.error is None

    field.set(3.5)
    field.validate()
    assert field.error is None

    field.set(5)
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": one_of}


@pytest.mark.parametrize("FieldType", [f.IntegerField, f.FloatField])
def test_invalid_one_of(FieldType):
    with pytest.raises(ValueError):
        FieldType(one_of="not a list")
