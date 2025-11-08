"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime
import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field


class DateField(Field):
    """
    A field that converts its input to a `datetime.date` without timezone.

    Args:
        format:
            The format of the date string. Defaults to '%Y-%m-%d'.
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        after_date:
            A date that the field value must be after. Defaults to `None`.
        before_date:
            A date that the field value must be before. Defaults to `None`.
        past_date:
            Whether the date must be in the past. Defaults to `False`.
        future_date:
            Whether the date must be in the future. Defaults to `False`.
        offset:
            Timezone offset in hours (floats are allowed) for calculating "today" when
            `past_date` or `future_date` are used. Defaults to `0` (UTC timezone).
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    def __init__(
        self,
        format="%Y-%m-%d",
        *,
        required: bool = True,
        default: t.Any = None,
        after_date: datetime.date | str | None = None,
        before_date: datetime.date | str | None = None,
        past_date: bool = False,
        future_date: bool = False,
        offset: int | float = 0,
        one_of: Iterable[t.Any] | None = None,
        messages: dict[str, str] | None = None,
        _utcnow: datetime.datetime | None = None,
    ):
        self.format = format

        if after_date and isinstance(after_date, str):
            after_date = self.filter_value(after_date)
        self.after_date = t.cast(datetime.date | None, after_date)

        if before_date and isinstance(before_date, str):
            before_date = self.filter_value(before_date)
        self.before_date = t.cast(datetime.date | None, before_date)

        self.past_date = past_date
        self.future_date = future_date

        if not isinstance(offset, (int, float)):
            raise ValueError("`offset` must be an integer or float representing hours")
        self.offset = offset

        # For easier testing
        self._utcnow = _utcnow

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
            one_of = [
                self.filter_value(date) if isinstance(date, str) else date
                for date in one_of
            ]
        self.one_of = one_of

        if isinstance(default, str):
            default = self.filter_value(default)

        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def filter_value(self, value: str | datetime.date | None) -> datetime.date | None:
        """
        Convert the value to a Python date.
        The date is expected to be in the format `DateField.format`.
        """
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, self.format).date()

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not self.value:
            return True

        if self.after_date and self.value <= self.after_date:
            self.error = err.AFTER_DATE
            self.error_args = {"after_date": self.after_date}
            return False
        if self.before_date and self.value >= self.before_date:
            self.error = err.BEFORE_DATE
            self.error_args = {"before_date": self.before_date}
            return False

        now = self._utcnow or datetime.datetime.now(datetime.timezone.utc)
        if self.offset:
            now += datetime.timedelta(hours=self.offset)
        today = now.date()

        if self.past_date and self.value >= today:
            self.error = err.PAST_DATE
            return False
        if self.future_date and self.value <= today:
            self.error = err.FUTURE_DATE
            return False

        if self.one_of and self.value not in self.one_of:
            self.error = err.ONE_OF
            self.error_args = {"one_of": self.one_of}
            return False

        return True
