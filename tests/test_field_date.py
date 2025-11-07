"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

import pytest

import formidable as f
from formidable import errors as err


def test_date_field():
    class TestForm(f.Form):
        birthday = f.DateField()
        anniversary = f.DateField(default="2020-01-01")

    form = TestForm({"birthday": ["1990-05-15"]})

    assert form.birthday.name == "birthday"
    assert form.birthday.value == datetime.date(1990, 5, 15)
    assert form.anniversary.value == datetime.date(2020, 1, 1)

    data = form.save()
    print(data)
    assert data == {
        "birthday": datetime.date(1990, 5, 15),
        "anniversary": datetime.date(2020, 1, 1),
    }


def test_callable_default():
    class TestForm(f.Form):
        birthday = f.DateField(default=lambda: datetime.date(2000, 1, 1))

    form = TestForm()
    assert form.birthday.value == datetime.date(2000, 1, 1)


def test_validate_date_past_date():
    field = f.DateField(past_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("2023-10-01")
    field.validate()
    assert field.error is None

    field.set("2026-01-01")
    field.validate()
    assert field.error == err.PAST_DATE
    assert field.error_args is None


def test_validate_date_future_date():
    field = f.DateField(future_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("2026-01-01")
    field.validate()
    assert field.error is None

    field.set("2023-10-01")
    field.validate()
    assert field.error == err.FUTURE_DATE
    assert field.error_args is None


def test_validate_date_future_date_with_offset():
    field = f.DateField(future_date=True, offset=-5, _utcnow=datetime.datetime(2025, 1, 1, 3, 49, 0))

    field.set("2025-01-01")
    field.validate()
    assert field.error is None

    field.set("2024-12-31")
    field.validate()
    assert field.error == err.FUTURE_DATE
    assert field.error_args is None


def test_date_invalid_offset():
    with pytest.raises(ValueError):
        f.DateField(offset="not an int")  # type: ignore


def test_validate_date_after_date():
    field = f.DateField(after_date="2023-10-01")

    field.set("2023-10-02")
    field.validate()
    assert field.error is None

    field.set("2023-09-30")
    field.validate()
    assert field.error == err.AFTER_DATE
    assert field.error_args == {"after_date": datetime.date(2023, 10, 1)}

    field.set("2023-10-01")
    field.validate()
    assert field.error == err.AFTER_DATE
    assert field.error_args == {"after_date": datetime.date(2023, 10, 1)}


def test_invalid_date_after_date():
    with pytest.raises(ValueError):
        f.DateField(after_date="not a date")


def test_validate_date_before_date():
    field = f.DateField(before_date="2023-10-01")

    field.set("2023-09-30")
    field.validate()
    assert field.error is None

    field.set("2023-10-01")
    field.validate()
    assert field.error == err.BEFORE_DATE
    assert field.error_args == {"before_date": datetime.date(2023, 10, 1)}

    field.set("2023-10-02")
    field.validate()
    assert field.error == err.BEFORE_DATE
    assert field.error_args == {"before_date": datetime.date(2023, 10, 1)}


def test_invalid_date_before_date():
    with pytest.raises(ValueError):
        f.DateField(before_date="not a date")


def test_validate_date_one_of():
    one_of = [
        datetime.date(2025, 5, 5),
        "2024-05-05",
        datetime.date(2023, 5, 5),
    ]
    field = f.DateField(one_of=one_of)

    field.set("2024-05-05")
    field.validate()
    assert field.error is None

    field.set("2026-01-01")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {
        "one_of": [
            datetime.date(2025, 5, 5),
            datetime.date(2024, 5, 5),
            datetime.date(2023, 5, 5),
        ]
    }


def test_invalid_date_one_of():
    with pytest.raises(ValueError):
        f.DateField(one_of="not a date list")

    with pytest.raises(ValueError):
        f.DateField(one_of=["a", "b", "c"])  # Invalid date types
