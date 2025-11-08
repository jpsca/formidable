"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .. import errors as err
from .base import Field


class FileField(Field):
    """
    A field for rendering a file input.

    **This field does not perform any processing or uploading**.

    Your web framework typically doesn't even make the file data available
    in the request object, just the filename(s), so you are responsible for
    handling the uploaded file data in the view/controller that processes
    the form submission.

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

        try:
            value = self._custom_filter(value)
        except ValueError as e:
            self.error = e.args[0] if e.args else err.INVALID
            self.error_args = e.args[1] if len(e.args) > 1 else None
            return

        self.value = self.filter_value(value)
        if self.required and value in [None, ""]:
            self.error = err.REQUIRED
            return

    def filter_value(self, value: t.Any) -> t.Any:
        return value
