"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

from .base import Field


class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value: str | bool | None) -> bool:
        """
        Convert the value to a Python boolean type.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ("true", "1", "yes"):
                return True
            elif value in ("", "false", "0", "no"):
                return False
        raise ValueError(f"Invalid boolean value: {value}")
