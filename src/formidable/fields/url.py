"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import TCustomValidator
from .text import TextField


class URLField(TextField):

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        schemes: Iterable[str] | None = None,
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
        self.schemes = schemes or ["http", "https"]
        self.rx_url = self._compile_url_regex(schemes=self.schemes)

    def _compile_url_regex(self, schemes: Iterable[str]) -> t.Pattern[str]:
        """
        Compile a regex pattern for validating URLs based on the provided schemes.
        Args:
            schemes: Iterable of URL schemes to include in the regex.
        Returns:
            Compiled regex pattern for URL validation.
        """
        import re
        scheme_pattern = "|".join(schemes)
        return re.compile(
            rf"^(?:(?:{scheme_pattern}):\/\/)(?:[a-zA-Z0-9\-._~!$&'()*+,;=:@]+)(?:\/[a-zA-Z0-9\-._~!$&'()*+,;=:@]*)*$"
        )

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not super().validate_value():
            return False

        if not self.value or self.error:
            return False

        if not self.rx_url.match(self.value):
            self.error = err.INVALID_URL
            return False

        return True
