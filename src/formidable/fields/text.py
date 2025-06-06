"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

from .base import Field


class TextField(Field):
    """
    A text field for forms.
    This field is used to capture text input from users.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_python(self, value: str) -> str:
        """
        Convert the value to a Python string type.
        """
        if value is None:
            return None
        return str(value).strip()
