"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

import pytest

import formidable as f
from formidable import errors as err


def test_time_field():
    class TestForm(f.Form):
        start = f.TimeField()
        end = f.TimeField(default="17:00:00")

    form = TestForm({"start": ["09:15:00"]})

    assert form.start.name == "start"
    assert form.start.value == datetime.time(9, 15, 0)
    assert form.end.value == datetime.time(17, 0, 0)

    data = form.save()
    print(data)
    assert data == {
        "start": datetime.time(9, 15, 0),
        "end": datetime.time(17, 0, 0),
    }


def test_time_field_precision():
    field = f.TimeField()

    field.set("14")
    assert field.value == datetime.time(14, 0)

    field.set("14:30")
    assert field.value == datetime.time(14, 30)

    field.set("14:30:45")
    assert field.value == datetime.time(14, 30, 45)


def test_time_am_pm():
    field = f.TimeField()

    field.set("2 PM")
    assert field.value == datetime.time(14, 0)

    field.set("2 AM")
    assert field.value == datetime.time(2, 0)

    field.set("3:30 PM")
    assert field.value == datetime.time(15, 30)

    field.set("3:30:45 AM")
    assert field.value == datetime.time(3, 30, 45)


def test_time_threshold():
    field = f.TimeField()

    field.set("12 AM")
    assert field.value == datetime.time(0, 0)

    field.set("12 PM")
    assert field.value == datetime.time(12, 0)


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


def test_invalid_time_format():
    field = f.TimeField()

    field.set("not a time")
    field.validate()
    assert field.error == err.INVALID
    assert field.error_args is None

    field.set("25:00")
    field.validate()
    assert field.error == err.INVALID
    assert field.error_args is None

    field.set("12:60")
    field.validate()
    assert field.error == err.INVALID
    assert field.error_args is None


def test_validate_one_of():
    field = f.TimeField(one_of=[
        "12:00",
        datetime.time(13),
        "14:00",
    ])

    field.set("12:00")
    field.validate()
    assert field.error is None

    field.set("13:00:00")
    field.validate()
    assert field.error is None

    field.set("2 PM")
    field.validate()
    assert field.error is None

    field.set("15:00")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {
        "one_of": [
            datetime.time(12),
            datetime.time(13),
            datetime.time(14),
        ]}


def test_invalid_one_of():
    with pytest.raises(ValueError):
        f.TimeField(one_of="not a list")

    with pytest.raises(ValueError):
        f.TimeField(one_of=["a", "b"])  # Invalid time values
