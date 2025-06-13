"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field, TCustomValidator


class ListField(Field):
    # The value of this field is a list of values.
    multiple: bool = True

    def __init__(
        self,
        type: t.Any = None,
        *,
        required: bool = True,
        default: t.Any = None,
        min_items: int | None = None,
        max_items: int | None = None,
        before: Iterable[TCustomValidator] | None = None,
        after: Iterable[TCustomValidator] | None = None,
        one_of: Iterable[t.Any] | None = None,
        messages: dict[str, str] | None = None,
    ):
        """
        A field that represents a list of items.

        Args:
            type:
                The type of items in the list. Defaults to `None` (no casting).
            required:
                Whether the field is required. Defaults to `True`.
            default:
                Default value for the field. Defaults to `[]`.
            min_items:
                Minimum number of items in the list. Defaults to None (no minimum).
            max_items:
                Maximum number of items in the list. Defaults to None (no maximum).
            before:
                List of custom validators to run before setting the value.
            after:
                List of custom validators to run after setting the value.
            one_of:
                List of values that the field value must be one of. Defaults to `None`.
            messages:
                Overrides of the error messages, specifically for this field.

        """
        self.type = type

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
            before=before,
            after=after,
            messages=messages,
        )

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[]"

    def to_python(self, value: t.Any) -> t.Any:
        """
        Convert the value to a Python type.
        """
        if self.type is None:
            return value

        # TODO: Accept an instance of a Field subclass as type
        if isinstance(value, list):
            return [self.type(item) for item in value]
        else:
            return [self.type(value)]

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
