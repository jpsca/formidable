"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

import pytest

import formidable as f
from formidable import errors as err


def test_datetime_field():
    class TestForm(f.Form):
        created = f.DateTimeField()
        updated = f.DateTimeField(default="2024-06-05T12:34:56")

    form = TestForm({"created": ["2025-06-05T08:30:00"]})

    assert form.created.name == "created"
    assert form.created.value == datetime.datetime(2025, 6, 5, 8, 30)
    assert form.updated.value == datetime.datetime(2024, 6, 5, 12, 34, 56)

    data = form.save()
    print(data)
    assert data == {
        "created": datetime.datetime(2025, 6, 5, 8, 30),
        "updated": datetime.datetime(2024, 6, 5, 12, 34, 56),
    }


def test_callable_default():
    class TestForm(f.Form):
        created = f.DateTimeField(default=lambda: datetime.datetime(2025, 1, 1, 12, 0, 0))

    form = TestForm()
    assert form.created.value == datetime.datetime(2025, 1, 1, 12, 0)


def test_validate_datetime_past_date():
    field = f.DateTimeField(
        past_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0)
    )

    field.set("2023-10-01T12:00:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T11:50:00")
    field.validate()
    assert field.error == err.PAST_DATE
    assert field.error_args is None


def test_validate_datetime_future_date():
    field = f.DateTimeField(
        future_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0)
    )

    field.set("2025-01-01T12:50:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T11:40:00")
    field.validate()
    assert field.error == err.FUTURE_DATE
    assert field.error_args is None


def test_validate_datetime_past_date_with_offset():
    field = f.DateTimeField(
        past_date=True, offset=-5, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0)
    )

    field.set("2023-10-01T07:00:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T06:50:00")
    field.validate()
    assert field.error == err.PAST_DATE
    assert field.error_args is None


def test_validate_datetime_future_date_with_offset():
    field = f.DateTimeField(
        future_date=True, offset=-5, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0)
    )

    field.set("2025-01-01T07:50:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T06:40:00")
    field.validate()
    assert field.error == err.FUTURE_DATE
    assert field.error_args is None


def test_datetime_invalid_offset():
    with pytest.raises(ValueError):
        f.DateTimeField(offset="not an int")  # type: ignore


def test_validate_datetime_after_date():
    field = f.DateTimeField(after_date="2023-10-01T00:00:00")

    field.set("2023-10-02T00:00:00")
    field.validate()
    assert field.error is None

    field.set("2023-10-01T00:00:00")
    field.validate()
    assert field.error == err.AFTER_DATE
    assert field.error_args == {"after_date": datetime.datetime(2023, 10, 1)}

    field.set("2023-09-30T00:00:00")
    field.validate()
    assert field.error == err.AFTER_DATE
    assert field.error_args == {"after_date": datetime.datetime(2023, 10, 1)}


def test_invalid_datetime_after_date():
    with pytest.raises(ValueError):
        f.DateTimeField(after_date="not a date")


def test_validate_datetime_before_date():
    field = f.DateTimeField(before_date="2023-10-01T00:00:00")

    field.set("2023-09-30T00:00:00")
    field.validate()
    assert field.error is None

    field.set("2023-10-01T00:00:00")
    field.validate()
    assert field.error == err.BEFORE_DATE
    assert field.error_args == {"before_date": datetime.datetime(2023, 10, 1)}

    field.set("2023-10-02T00:00:00")
    field.validate()
    assert field.error == err.BEFORE_DATE
    assert field.error_args == {"before_date": datetime.datetime(2023, 10, 1)}


def test_invalid_datetime_before_date():
    with pytest.raises(ValueError):
        f.DateTimeField(before_date="not a date")


def test_validate_datetime_one_of():
    one_of = [
        datetime.datetime(2025, 5, 5),
        datetime.datetime(2024, 5, 5),
        "2023-05-05T00:00:00",
    ]
    field = f.DateTimeField(one_of=one_of)

    field.set("2024-05-05T00:00:00")
    field.validate()
    assert field.error is None

    field.set("2024-05-05T10:03:00")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {
        "one_of": [
            datetime.datetime(2025, 5, 5),
            datetime.datetime(2024, 5, 5),
            datetime.datetime(2023, 5, 5),
        ]
    }


def test_invalid_datetime_one_of():
    with pytest.raises(ValueError):
        f.DateTimeField(one_of="not a date list")

    with pytest.raises(ValueError):
        f.DateTimeField(one_of=["a", "b", "c"])  # Invalid date types
