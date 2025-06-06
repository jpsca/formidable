"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .. import errors as err
from .base import Field


class ListField(Field):
    def __init__(
        self,
        type: t.Any = None,
        *,
        required: bool = True,
        default: list | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
    ):
        """
        A field that represents a list of items.

        Arguments:

        - type: The type of items in the list. Defaults to `None` (no casting).
        - required: Whether the field is required. Defaults to `True`.
        - default: Default value for the field. Defaults to `[]`.
        - min_items: Minimum number of items in the list. Defaults to None (no minimum).
        - max_items: Maximum number of items in the list. Defaults to None (no maximum).

        """
        self.type = type

        if min_items is not None and (not isinstance(min_items, int) or min_items < 0):
            raise ValueError("`min_items` must be a positive integer")
        self.min_items = min_items

        if max_items is not None and (not isinstance(max_items, int) or max_items < 0):
            raise ValueError("`max_items` must be a positive integer")
        self.max_items = max_items

        default = default if default is not None else []
        if not isinstance(default, list):
            raise ValueError("`default` must be a list or `None`")
        super().__init__(required=required, default=default)

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[]"

    def to_python(self, value: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        if value is None:
            return None
        if self.type is not None:
            if isinstance(value, list):
                return [self.type(item) for item in value]
            else:
                return [self.type(value)]
        return value

    def validate(self):
        """
        Validate the field value against the defined constraints.
        """
        super().validate()
        if self.error:
            return False

        if not isinstance(self.value, list):
            self.error = err.INVALID
            return False

        if self.min_items is not None and len(self.value) < self.min_items:
            self.error = err.MIN_ITEMS
            self.error_args = {"min_items": self.min_items}
            return False

        if self.max_items is not None and len(self.value) > self.max_items:
            self.error = err.MAX_ITEMS
            self.error_args = {"max_items": self.max_items}
            return False

        return True
