"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .. import errors as err
from .base import Field


if t.TYPE_CHECKING:
    from ..form import Form


class FormField(Field):
    def __init__(
        self,
        form_cls: "type[Form]",
        *,
        required: bool = True,
        default: dict | None = None,
    ):
        """
        A field that represents a single sub-form.

        Args:
            form_cls: The class of the form to be used as a sub-form.
            required: Whether the field is required. Defaults to `True`.
            default: Default value for the field. Defaults to `None`.

        """
        self.form = form_cls()

        if default is not None and not isinstance(default, dict):
            raise ValueError("`default` must be a dictionary or `None`")
        super().__init__(required=required, default=default)

    def set_messages(self, messages: dict[str, str]):
        self.form._set_messages(messages)

    def set_name_format(self, name_format: str):
        self.name_format = name_format
        sub_name_format = f"{self.name}[{{name}}]"
        self.form._set_name_format(sub_name_format)

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        if not (reqvalue or objvalue):
            if self.default_value is not None:
                reqvalue = self.default_value
            elif self.required:
                self.error = err.REQUIRED

        self.form._set(reqvalue, objvalue)

    def validate_value(self) -> bool:
        valid = self.form.validate()
        if not valid:
            self.error = self.form.get_errors()
        return valid

    def save(self) -> t.Any:
        return self.form.save()
