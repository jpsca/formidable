"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .base import Field


if t.TYPE_CHECKING:
    from ..form import Form


class FormField(Field):
    """
    A field that represents a form
    """

    def __init__(self, form_cls: "type[Form]", **kwargs):
        super().__init__(**kwargs)
        self.form = form_cls()

    def set_messages(self, messages: dict[str, str]):
        self.form._set_messages(messages)

    def set_name_format(self, name_format: str):
        self.name_format = name_format
        sub_name_format = f"{self.name}[{{name}}]"
        self.form._set_name_format(sub_name_format)

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.form._set(reqvalue, objvalue)

    def validate(self) -> bool:
        valid = self.form.validate()
        if not valid:
            self.error = self.form.get_errors()
        return valid

    def save(self) -> t.Any:
        return self.form.save()
