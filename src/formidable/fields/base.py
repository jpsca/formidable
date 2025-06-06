"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t


if t.TYPE_CHECKING:
    from ..form import Form



class Field:
    parent: "Form | None" = None
    name_format: str = "{name}"
    field_name: str = ""
    default: t.Any = None
    value: t.Any = None
    error: str | dict[str, t.Any] | None = None
    messages: dict[str, str]

    ERROR_INVALID = "invalid"
    ERROR_REQUIRED = "required"

    def __init__(self, *, required: bool = True, default: t.Any = None):
        """
        Base class for all form fields.

        Arguments:
        - required: Whether the field is required. Defaults to True.
        - default: Default value for the field. Defaults to None.

        """
        self.required = required
        self.default = default
        self.value = self.default_value
        self.error = None
        self.messages = {}

    def __repr__(self):
        attrs = [
            f"name={self.name!r}",
            f"value={self.value!r}",
            f"default={self.default!r}",
            f"error={self.error!r}",

        ]
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @property
    def name(self) -> str:
        return self.name_format.format(name=self.field_name)

    @property
    def error_message(self) -> str:
        """
        Returns the error message for the field, if any.
        """
        if not isinstance(self.error, str):
            return ""
        return self.messages.get(self.error, self.error)

    @property
    def default_value(self) -> t.Any:
        """
        Calculates the default value of the field, if default is a callable.
        """
        if callable(self.default):
            return self.default()
        return self.default

    def set_messages(self, messages: dict[str, str]):
        self.messages = messages

    def set_name_format(self, name_format: str):
        self.name_format = name_format

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error =  None
        value = objvalue if reqvalue is None else reqvalue
        if value is None:
            value = self.default_value
        try:
            self.value = self.to_python(value)
        except (ValueError, TypeError):
            self.error = self.ERROR_INVALID
            self.value = self.default_value

    def to_python(self, value: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        return value

    def validate(self) -> bool:
        """
        Validate the value of the field.
        """
        if self.error is not None:
            return False
        if self.required and self.value is None:
            self.error = self.ERROR_REQUIRED
            return False
        return True

    def save(self) -> t.Any:
        return self.value
