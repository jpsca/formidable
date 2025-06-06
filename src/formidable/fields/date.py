"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime

from .base import Field


class DateField(Field):
    def __init__(self, format="%Y-%m-%d", **kwargs):
        super().__init__(**kwargs)
        self.format = format

    def to_python(self, value: str) -> datetime.date | None:
        """
        Convert the value to a Python date.
        The date is expected to be in the format 'YYYY-MM-DD'.
        """
        if not value:
            return None
        return datetime.datetime.strptime(value, self.format).date()


class DateTimeField(DateField):
    def __init__(self, format="%Y-%m-%dT%H:%M:%S", **kwargs):
        super().__init__(**kwargs)
        self.format = format

    def to_python(self, value: str) -> datetime.datetime | None:
        """
        Convert the value to a Python datetime.
        The datetime is expected to be in the format 'YYYY-MM-DDTHH:MM:SS'.
        """
        if not value:
            return None
        return datetime.datetime.strptime(value, self.format)
