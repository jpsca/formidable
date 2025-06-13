"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import re
import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import TCustomValidator
from .text import TextField


class SlugField(TextField):

    rx_slug = re.compile(r"^[-a-zA-Z0-9_]+\Z")

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        before: Iterable[TCustomValidator] | None = None,
        after: Iterable[TCustomValidator] | None = None,
        one_of: Iterable[str] | None = None,
        messages: dict[str, str] | None = None,
    ):
        """
        A field for validating URLs.

        Args:
            required:
                Whether the field is required. Defaults to `True`.
            default:
                Default value for the field. Defaults to `None`.
            schemes:
                URL/URI scheme list to validate against. If not provided,
                the default list is ["http", "https"].
            min_length:
                Minimum length of the text. Defaults to `None `(no minimum).
            max_length:
                Maximum length of the text. Defaults to `None` (no maximum).
            pattern:
                A regex pattern that the string must match. Defaults to `None`.
            before:
                List of custom validators to run before setting the value.
            after:
                List of custom validators to run after setting the value.
            one_of:
                List of values that the field value must be one of. Defaults to `None`.
            messages:
                Overrides of the error messages, specifically for this field.

        """
        super().__init__(
            required=required,
            default=default,
            before=before,
            after=after,
            one_of=one_of,
            messages=messages
        )

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not super().validate_value():
            return False

        if not self.value or self.error:
            return False

        if not self.rx_slug.match(self.value):
            self.error = err.INVALID_SLUG
            return False

        return True
