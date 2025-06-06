"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import re

from .. import errors as err
from .base import Field


class TextField(Field):
    def __init__(
        self,
        *,
        required: bool = True,
        default: str | None = None,
        strip: bool = True,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
    ):
        """
        A text field for forms.
        This field is used to capture text input from users.

        Arguments:

        - required: Whether the field is required. Defaults to `True`.
        - default: Default value for the field. Defaults to `None`.
        - strip: Whether to strip whitespace from the text. Defaults to `True`.
        - min_length: Minimum length of the text. Defaults to `None `(no minimum).
        - max_length: Maximum length of the text. Defaults to `None` (no maximum).
        - pattern: A regex pattern that the string must match. Defaults to `None`.

        """
        self.strip = strip

        if min_length is not None and not isinstance(min_length, int):
            raise ValueError("`min_length` must be an integer")
        self.min_length = min_length

        if max_length is not None and not isinstance(max_length, int):
            raise ValueError("`max_length` must be an integer")
        self.max_length = max_length

        if pattern is not None:
            try:
                re.compile(pattern)
            except (TypeError, ValueError, re.error) as e:
                raise ValueError("Invalid regex pattern") from e
        self.pattern = pattern

        default = str(default) if default is not None else None
        super().__init__(required=required, default=default)

    def to_python(self, value: str | None) -> str | None:
        """
        Convert the value to a Python string type.
        """
        if value is None:
            return None
        value = str(value)
        if self.strip:
            value = value.strip()
        return value

    def validate(self):
        """
        Validate the field value against the defined constraints.
        """
        super().validate()
        if self.error:
            return False

        if self.min_length is not None and len(self.value) < self.min_length:
            self.error = err.MIN_LENGTH
            self.error_args = {"min_length": self.min_length}
            return False

        if self.max_length is not None and len(self.value) > self.max_length:
            self.error = err.MAX_LENGTH
            self.error_args = {"max_length": self.max_length}
            return False

        if self.pattern and not re.match(self.pattern, self.value):
            self.error = err.PATTERN
            self.error_args = {"pattern": self.pattern}
            return False

        return True
