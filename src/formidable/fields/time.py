"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime
import re
import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field


class TimeField(Field):
    """
    A field that converts its input to a `datetime.time` without timezone.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        after_time:
            A time that the field value must be after. Defaults to `None`.
        before_time:
            A time that the field value must be before. Defaults to `None`.\
        past_time:
            Whether the time must be in the past. Defaults to `False`.
        future_time:
            Whether the time must be in the future. Defaults to `False`.
        offset:
            Timezone offset in hours (floats are allowed) for calculating "now" when
            `past_time` or `future_time` are used. Defaults to `0` (UTC timezone).
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    RX_TIME = re.compile(
        (
            r"^(?:"
            r"(?P<hour>[0-2]?[0-9])"
            r"|(?P<hour12>[0-2]?[0-9])\s*(?P<tt>am|pm)"
            r"|(?P<hour_min>[0-2]?[0-9]):(?P<minute>[0-5][0-9])"
            r"|(?P<hour12_min>[0-2]?[0-9]):(?P<minute12>[0-5][0-9])\s*(?P<tt_min>am|pm)"
            r"|(?P<hour_sec>[0-2]?[0-9]):(?P<minute_sec>[0-5][0-9]):(?P<second>[0-5][0-9])"
            r"|(?P<hour12_sec>[0-2]?[0-9]):(?P<minute12_sec>[0-5][0-9]):(?P<second12>[0-5][0-9])\s*(?P<tt_sec>am|pm)"
            r")$"
        ),
        re.IGNORECASE,
    )

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        after_time: datetime.time | str | None = None,
        before_time: datetime.time | str | None = None,
        past_time: bool = False,
        future_time: bool = False,
        offset: int | float = 0,
        one_of: Iterable[t.Any] | None = None,
        messages: dict[str, str] | None = None,
        _utcnow: datetime.datetime | None = None,
    ):
        self.format = format

        if after_time and isinstance(after_time, str):
            after_time = self.filter_value(after_time)
        self.after_time = t.cast(datetime.time | None, after_time)

        if before_time and isinstance(before_time, str):
            before_time = self.filter_value(before_time)
        self.before_time = t.cast(datetime.time | None, before_time)

        self.past_time = past_time
        self.future_time = future_time
        self.offset = offset

        # For easier testing
        self._utcnow = _utcnow

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
            one_of = [
                self.filter_value(time) if isinstance(time, str) else time
                for time in one_of if time is not None
            ]
        self.one_of = one_of

        if default is not None and isinstance(default, str):
            default = self.filter_value(default)

        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def filter_value(self, value: str | datetime.time | None) -> datetime.time | None:
        """
        Convert the value to a Python time type.
        """
        if value is None:
            return None
        if isinstance(value, datetime.time):
            return value

        match = self.RX_TIME.match(value.strip())
        if not match:
            raise ValueError(f"Invalid time value: {value}")

        try:
            gd = match.groupdict()

            # Get hour from whichever pattern matched
            hour = int(
                gd.get("hour")
                or gd.get("hour12")
                or gd.get("hour_min")
                or gd.get("hour12_min")
                or gd.get("hour_sec")
                or gd.get("hour12_sec")
                or 0
            )
            # Get minute from whichever pattern matched (or default to 0)
            minute = int(
                gd.get("minute")
                or gd.get("minute12")
                or gd.get("minute_sec")
                or gd.get("minute12_sec")
                or 0
            )
            # Get second (or default to 0)
            second = int(
                gd.get("second")
                or gd.get("second12")
                or 0
            )
            # Get AM/PM from whichever pattern matched
            tt = (gd.get("tt") or gd.get("tt_min") or gd.get("tt_sec") or "").strip().upper()

            # Handle AM/PM
            if tt == "PM" and hour < 12:
                hour += 12
            elif tt == "AM" and hour == 12:
                hour = 0

            return datetime.time(hour, minute, second)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid time value: {value}") from None

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not self.value:
            return True

        if self.after_time and self.value <= self.after_time:
            self.error = err.AFTER_TIME
            self.error_args = {"after_time": self.after_time}
            return False

        if self.before_time and self.value >= self.before_time:
            self.error = err.BEFORE_TIME
            self.error_args = {"before_time": self.before_time}
            return False

        now = self._utcnow or datetime.datetime.now(datetime.timezone.utc)
        if self.offset:
            now += datetime.timedelta(hours=self.offset)
        now = now.time()

        if self.past_time and self.value >= now:
            self.error = err.PAST_TIME
            return False

        if self.future_time and self.value <= now:
            self.error = err.FUTURE_TIME
            return False

        if self.one_of and self.value not in self.one_of:
            self.error = err.ONE_OF
            self.error_args = {"one_of": self.one_of}
            return False

        return True
