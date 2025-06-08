"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

from .base import Field, TCustomValidator


class BooleanField(Field):
    FALSE_VALUES = ("false", "0", "no")

    def __init__(
        self,
        *,
        default: bool | str | None = None,
        before: list[TCustomValidator] | None = None,
        after: list[TCustomValidator] | None = None,
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
            default: Default value for the field. Defaults to `None`.
            before: List of custom validators to run before setting the value.
            after: List of custom validators to run after setting the value.

        """
        if default is not None and not isinstance(default, bool):
            raise ValueError("`default` must be a boolean or `None`")
        super().__init__(default=default, before=before, after=after)

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
