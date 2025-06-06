"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .base import Field


class ListField(Field):
    def __init__(self, type: t.Any = None, **kwargs):
        """
        A field that represents a list of items.

        Arguments:
        - type: The type of items in the list. Defaults to None, no casting is attempted.

        """
        kwargs.setdefault("default", list)
        super().__init__(**kwargs)
        self.type = type

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[]"

    def to_python(self, value: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        if self.type is not None:
            if isinstance(value, list):
                return [self.type(item) for item in value]
            else:
                return [self.type(value)]
        return value
