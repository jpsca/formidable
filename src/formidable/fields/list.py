"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field


class ListField(Field):
    """
    A field that represents a list of same-type values.

    This is the field to use when you expect multiple values for a single field, like
    a `<select multiple>` HTML input or a group of checkboxes with the same name.

    A `type` is a function used to cast the items in the list. It can be a simple Python
    type like `int` or it can be your own function.

    If `strict` is `True`, any casting error will raise an exception. If `strict` is
    `False` (the default), the error will be ignored and the value will not be added
    to the final list.

    Args:
        type:
            A callable that is used to cast the items in the list. Defaults to `None` (no casting).
        strict:
            Whether to enforce strict type checking. Defaults to `False`.
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `[]`.
        min_items:
            Minimum number of items in the list. Defaults to None (no minimum).
        max_items:
            Maximum number of items in the list. Defaults to None (no maximum).
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    # The value of this field is a list of values.
    multiple: bool = True

    def __init__(
        self,
        type: t.Any = None,
        *,
        strict: bool = False,
        required: bool = True,
        default: t.Any = None,
        min_items: int | None = None,
        max_items: int | None = None,
        one_of: Iterable[t.Any] | None = None,
        messages: dict[str, str] | None = None,
    ):
        self.type = type
        self.strict = strict

        if min_items is not None and (not isinstance(min_items, int) or min_items < 0):
            raise ValueError("`min_items` must be a positive integer")
        self.min_items = min_items

        if max_items is not None and (not isinstance(max_items, int) or max_items < 0):
            raise ValueError("`max_items` must be a positive integer")
        self.max_items = max_items

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
        self.one_of = one_of

        default = default if default is not None else []

        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[]"

    def filter_value(self, items: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        if not isinstance(items, list):
            items = [items]

        if self.type is None:
            return items

        values = []
        for item in items:
            try:
                values.append(self.type(item))
            except Exception as e:
                if self.strict:
                    raise e

        return values

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if self.min_items is not None and len(self.value) < self.min_items:
            self.error = err.MIN_ITEMS
            self.error_args = {"min_items": self.min_items}
            return False

        if self.max_items is not None and len(self.value) > self.max_items:
            self.error = err.MAX_ITEMS
            self.error_args = {"max_items": self.max_items}
            return False

        if self.one_of:
            for value in self.value:
                if value not in self.one_of:
                    self.error = err.ONE_OF
                    self.error_args = {"one_of": self.one_of}
                    return False

        return True
