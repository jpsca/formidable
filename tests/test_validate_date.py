"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

import pytest

import formidable as f
from formidable import errors as err


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


def test_validate_datetime_past_date():
    field = f.DateTimeField(past_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("2023-10-01T12:00:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T11:50:00")
    field.validate()
    assert field.error == err.PAST_DATE
    assert field.error_args is None


def test_validate_datetime_future_date():
    field = f.DateTimeField(future_date=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("2025-01-01T12:50:00")
    field.validate()
    assert field.error is None

    field.set("2025-01-01T11:40:00")
    field.validate()
    assert field.error == err.FUTURE_DATE
    assert field.error_args is None


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
