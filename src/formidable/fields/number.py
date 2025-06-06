"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

from .base import Field


class NumberField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class FloatField(NumberField):
    def to_python(self, value: str) -> float:
        """
        Convert the value to a Python float type.
        """
        if value is None:
            return None
        return float(value)


class IntegerField(NumberField):
    def to_python(self, value: str) -> int:
        """
        Convert the value to a Python integer type.
        """
        if value is None:
            return None
        return int(value)
