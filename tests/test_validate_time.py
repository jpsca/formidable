"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

import pytest

import formidable as f
from formidable import errors as err


def test_validate_past_time():
    field = f.TimeField(past_time=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("11:10")
    field.validate()
    assert field.error is None

    field.set("12:10")
    field.validate()
    assert field.error == err.PAST_TIME
    assert field.error_args is None

    field.set("11:49")
    field.validate()
    assert field.error == err.PAST_TIME
    assert field.error_args is None


def test_validate_past_time_offset():
    field = f.TimeField(past_time=True, offset=2, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("13:10")
    field.validate()
    assert field.error is None

    field.set("14:10")
    field.validate()
    assert field.error == err.PAST_TIME
    assert field.error_args is None

    field.set("13:49")
    field.validate()
    assert field.error == err.PAST_TIME
    assert field.error_args is None


def test_validate_future_time():
    field = f.TimeField(future_time=True, _utcnow=datetime.datetime(2025, 1, 1, 11, 49, 0))

    field.set("23:59")
    field.validate()
    assert field.error is None

    field.set("00:00")
    field.validate()
    assert field.error == err.FUTURE_TIME
    assert field.error_args is None

    field.set("11:49")
    field.validate()
    assert field.error == err.FUTURE_TIME
    assert field.error_args is None


def test_validate_after_time():
    field = f.TimeField(after_time="12:00")

    field.set("12:01")
    field.validate()
    assert field.error is None

    field.set("12:00")
    field.validate()
    assert field.error == err.AFTER_TIME
    assert field.error_args == {"after_time": datetime.time(12, 0)}

    field.set("11:59")
    field.validate()
    assert field.error == err.AFTER_TIME
    assert field.error_args == {"after_time": datetime.time(12, 0)}


def test_invalid_after_time():
    with pytest.raises(ValueError):
        f.TimeField(after_time="not a time")


def test_validate_before_time():
    field = f.TimeField(before_time="12:00")

    field.set("11:59")
    field.validate()
    assert field.error is None

    field.set("12:00")
    field.validate()
    assert field.error == err.BEFORE_TIME
    assert field.error_args == {"before_time": datetime.time(12, 0)}

    field.set("12:00")
    field.validate()
    assert field.error == err.BEFORE_TIME
    assert field.error_args == {"before_time": datetime.time(12, 0)}


def test_invalid_before_time():
    with pytest.raises(ValueError):
        f.TimeField(after_time="not a time")
