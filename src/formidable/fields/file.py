"""
Formable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .base import Field


class FileField(Field):
    def __init__(self, *, default: t.Any = None):
        """
        A field that represents a file upload.

        This field does not implement any special behavior nor accepts
        any validation rules. It serves as a placeholder for showing custom errors.

        """
        super().__init__(required=False, default=default)

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None

        # Not sent
        if reqvalue is None:
            self.value = self.default_value if objvalue is None else objvalue

        # Sent, but if empty, stored value takes precedence
        elif objvalue is not None:
            self.value = reqvalue or objvalue

        else:
            self.value = reqvalue

