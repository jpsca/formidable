"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err


if t.TYPE_CHECKING:
    from ..form import Form


TCustomValidator = t.Callable[[t.Any], t.Any]  # Type for a validator function


class Field:
    parent: "Form | None" = None
    name_format: str = "{name}"
    field_name: str = ""
    default: t.Any = None
    value: t.Any = None
    error: str | dict[str, t.Any] | None = None
    error_args: dict[str, t.Any] | None = None
    messages: dict[str, str]
    before: Iterable[TCustomValidator]
    after: Iterable[TCustomValidator]

    # Whether the value of this field is a list of values.
    multiple: bool = False

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        before: Iterable[TCustomValidator] | None = None,
        after: Iterable[TCustomValidator] | None = None,
        messages: dict[str, str] | None = None,
    ):
        """
        Base class for all form fields.

        Args:
            required:
                Whether the field is required. Defaults to `True`.
            default:
                Default value for the field. Defaults to `None`.
            before:
                List of custom validators to run before setting the value.
            after:
                List of custom validators to run after setting the value.
            messages:
                Overrides of the error messages, specifically for this field.

        """
        self.required = required
        self.default = default
        self.value = self.default_value
        self.messages = messages if messages is not None else {}
        self.before = before if before is not None else []
        self.after = after if after is not None else []

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
        if self.error is None or not isinstance(self.error, str):
            return ""
        tmpl = self.messages.get(self.error, err.MESSAGES.get(self.error, self.error))
        args = self.error_args or {}
        return tmpl.format(**args)

    @property
    def default_value(self) -> t.Any:
        """
        Calculates the default value of the field, if default is a callable.
        """
        if callable(self.default):
            return self.default()
        return self.default

    def set_messages(self, messages: dict[str, str]):
        self.messages = {**messages, **self.messages}

    def set_name_format(self, name_format: str):
        self.name_format = name_format

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None
        reqvalue = None if reqvalue == "" else reqvalue
        objvalue = None if objvalue == "" else objvalue

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

        try:
            self.value = self.to_python(value)
        except (ValueError, TypeError):
            self.error = err.INVALID
            return

        if self.required and self.value in [None, ""]:
            self.error = err.REQUIRED

    def to_python(self, value: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.to_python() must be implemented"
        )

    def validate(self) -> bool:
        """
        """
        if self.error is not None:
            return False

        self.validate_value()

        if self.error:
            return False

        for validator in self.after:
            try:
                self.value = validator(self.value)
            except ValueError as e:
                self.error = e.args[0] if e.args else err.INVALID
                self.error_args = e.args[1] if len(e.args) > 1 else None
                return False

        return True

    def validate_value(self) -> bool:
        return True

    def save(self) -> t.Any:
        return self.value
