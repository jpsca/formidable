"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field


class NumberField(Field):
    """
    A field that represents a number with optional constraints.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        gt:
            Value must be greater than this. Defaults to `None`.
        gte:
            Value must be greater than or equal to this. Defaults to `None`.
        lt:
            Value must be less than this. Defaults to `None`.
        lte:
            Value must be less than or equal to this. Defaults to `None`.
        multiple_of:
            Value must be a multiple of this. Defaults to `None`.
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        gt: int | float | None = None,
        gte: int | float | None = None,
        lt: int | float | None = None,
        lte: int | float | None = None,
        multiple_of: int | float | None = None,
        one_of: Iterable[t.Any] | None = None,
        messages: dict[str, str] | None = None,
    ):
        if gt is not None and not isinstance(gt, (int, float)):
            raise ValueError("`gt` must be an integer or float")
        self.gt = gt

        if gte is not None and not isinstance(gte, (int, float)):
            raise ValueError("`gte` must be an integer or float")
        self.gte = gte

        if lt is not None and not isinstance(lt, (int, float)):
            raise ValueError("`lt` must be an integer or float")
        self.lt = lt

        if lte is not None and not isinstance(lte, (int, float)):
            raise ValueError("`lte` must be an integer or float")
        self.lte = lte

        if multiple_of is not None and not isinstance(multiple_of, (int, float)):
            raise ValueError("`multiple_of` must be an integer or float")
        self.multiple_of = multiple_of

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
        self.one_of = one_of

        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not self.value:
            return True

        if self.gt is not None and self.value <= self.gt:
            self.error = err.GT
            self.error_args = {"gt": self.gt}
            return False

        if self.gte is not None and self.value < self.gte:
            self.error = err.GTE
            self.error_args = {"gte": self.gte}
            return False

        if self.lt is not None and self.value >= self.lt:
            self.error = err.LT
            self.error_args = {"lt": self.lt}
            return False

        if self.lte is not None and self.value > self.lte:
            self.error = err.LTE
            self.error_args = {"lte": self.lte}
            return False

        if self.multiple_of is not None and self.value % self.multiple_of != 0:
            self.error = err.MULTIPLE_OF
            self.error_args = {"multiple_of": self.multiple_of}
            return False

        if self.one_of and self.value not in self.one_of:
            self.error = err.ONE_OF
            self.error_args = {"one_of": self.one_of}
            return False

        return True


class FloatField(NumberField):
    """
    A field that converts its input to a float.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        gt:
            Value must be greater than this. Defaults to `None`.
        gte:
            Value must be greater than or equal to this. Defaults to `None`.
        lt:
            Value must be less than this. Defaults to `None`.
        lte:
            Value must be less than or equal to this. Defaults to `None`.
        multiple_of:
            Value must be a multiple of this. Defaults to `None`.
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    def filter_value(self, value: str | int | float | None) -> float | None:
        """
        Convert the value to a Python float type.
        """
        if value is None:
            return None
        return float(value)


class IntegerField(NumberField):
    """
    A field that converts its input to an integer.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        gt:
            Value must be greater than this. Defaults to `None`.
        gte:
            Value must be greater than or equal to this. Defaults to `None`.
        lt:
            Value must be less than this. Defaults to `None`.
        lte:
            Value must be less than or equal to this. Defaults to `None`.
        multiple_of:
            Value must be a multiple of this. Defaults to `None`.
        one_of:
            List of values that the field value must be one of. Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    def filter_value(self, value: str | int | float | None) -> int | None:
        """
        Convert the value to a Python integer type.
        """
        if value is None:
            return None
        return int(value)
