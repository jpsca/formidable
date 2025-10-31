"""
Formable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .. import errors as err
from .base import Field


class FileField(Field):
    """
    A field for rendering a file input.

    It does not perform any processing or uploading.
    """

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None

        # Not sent
        if reqvalue is None:
            value = self.default_value if objvalue is None else objvalue

        # Sent, but if empty, stored value takes precedence
        elif objvalue is not None:
            value = reqvalue or objvalue

        else:
            value = reqvalue

        for validator in self.before:
            try:
                value = validator(value)
            except ValueError as e:
                self.error = e.args[0] if e.args else err.INVALID
                self.error_args = e.args[1] if len(e.args) > 1 else None
                return

        self.value = self.to_python(value)
        if self.required and value in [None, ""]:
            self.error = err.REQUIRED
            return

    def to_python(self, value: t.Any) -> t.Any:
        return value
