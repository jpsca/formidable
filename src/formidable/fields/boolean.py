"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .. import errors as err
from .base import Field


class BooleanField(Field):
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
        required:
            Whether the field value *must* be `True`. Defaults to `False`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    FALSE_VALUES = ("false", "0", "no")

    def __init__(
        self,
        *,
        required: bool = False,
        default: t.Any = None,
        messages: dict[str, str] | None = None,
    ):
        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None

        value = objvalue if reqvalue is None else reqvalue
        if value is None:
            value = self.default_value

        try:
            value = self._custom_filter(value)
        except ValueError as e:
            self.error = e.args[0] if e.args else err.INVALID
            self.error_args = e.args[1] if len(e.args) > 1 else None
            return

        self.value = self.filter_value(value)

        if self.required and not self.value:
            self.error = err.REQUIRED

    def filter_value(self, value: str | bool | None) -> bool:
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


BoolField = BooleanField  # Alias
