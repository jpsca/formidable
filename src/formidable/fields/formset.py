"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .base import Field


if t.TYPE_CHECKING:
    from ..form import Form


class FormSet(Field):
    """
    A field that represents a set of forms, allowing for dynamic addition and removal of forms.
    """

    def __init__(self, form_cls: "type[Form]", **kwargs):
        super().__init__(**kwargs)
        self.form = form_cls()
        self.forms = []

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[NEW_INDEX]"
        sub_name_format = f"{self.name}[{{name}}]"
        self.form._set_name_format(sub_name_format)
