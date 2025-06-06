"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime
import re

from .base import Field


class TimeField(Field):
    """
    A field that represents a time value.
    """

    rx_time = re.compile(
        r"(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{1,2})(:(?P<second>[0-9]{1,2}))?\s?(?P<tt>am|pm)?",
        re.IGNORECASE,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value: str) -> datetime.time | None:
        """
        Convert the value to a Python time type.
        """
        if not value:
            return None
        match = self.rx_time.match(value.upper())
        if not match:
            raise ValueError(f"Invalid time value: {value}")
        try:
            gd = match.groupdict()
            hour = int(gd["hour"])
            minute = int(gd["minute"])
            second = int(gd["second"] or 0)
            if gd["tt"] == "PM":
                hour += 12
            return datetime.time(hour, minute, second)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid time value: {value}") from None
