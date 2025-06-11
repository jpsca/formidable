"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field, TCustomValidator


class BooleanField(Field):
    FALSE_VALUES = ("false", "0", "no")

    def __init__(
        self,
        *,
        default: t.Any = None,
        before: Iterable[TCustomValidator] | None = None,
        after: Iterable[TCustomValidator] | None = None,
        messages: dict[str, str] | None = None,
    ):
        """
        A field that represents a boolean value.

        Boolean fields are treated specially because of how browsers handle checkboxes:

        - If not checked: the browser doesn't send the field at all.
        - If checked: It sends the "value" attribute, but this is optional, so it could
          send an empty string instead.

        For these reasons:

        - A missing field (a `None` value) will become `False`.
        - A string value in the `FALSE_VALUES` tuple (case-insensitive) will become `False`.
        - Any other value, including an empty string, will become `True`.

        Args:
            default:
                Default value for the field. Defaults to `None`.
            before:
                List of custom validators to run before setting the value.
            after:
                List of custom validators to run after setting the value.
            messages:
                Overrides of the error messages, specifically for this field.

        """
        super().__init__(
            default=default,
            before=before,
            after=after,
            messages=messages,
        )

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None

        value = objvalue if reqvalue is None else reqvalue
        if value is None:
            value = self.default_value

        for validator in self.before:
            try:
                value = validator(value)
            except ValueError as e:
                self.error = e.args[0] if e.args else err.INVALID
                self.error_args = e.args[1] if len(e.args) > 1 else None
                return

        self.value = self.to_python(value)

    def to_python(self, value: str | bool | None) -> bool:
        """
        Convert the value to a Python boolean type.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in self.FALSE_VALUES:
                return False
        return True
