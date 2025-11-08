"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import re
import typing as t
from collections.abc import Iterable
from urllib.parse import urlsplit, urlunsplit

import idna

from .. import errors as err
from .base import Field


class URLField(Field):
    """
    A field for validating URLs.

    Even if the format is valid, it cannot guarantee that the URL is real. The
    purpose of this function is to alert the user of a typing mistake.

    Perform an UTS-46 normalization of the domain, which includes lowercasing
    (domain names are case-insensitive), NFC normalization, and converting all label
    separators (the period/full stop, fullwidth full stop, ideographic full stop, and
    halfwidth ideographic full stop) to basic periods.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        schemes:
            URL/URI scheme list to validate against. If not provided,
            the default list is ["http", "https"].
        pattern:
            A regex pattern that the string must match. Defaults to `None`.
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
        schemes: Iterable[str] | None = None,
        one_of: Iterable[str] | None = None,
        messages: dict[str, str] | None = None,
    ):
        self.schemes = schemes = schemes or ["http", "https"]
        self.rx_url = self._compile_url_regex(schemes=schemes)

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
        self.one_of = one_of

        default = str(default) if default is not None else None

        super().__init__(
            required=required,
            default=default,
            messages=messages,
        )

    def _compile_url_regex(self, schemes: Iterable[str]) -> t.Pattern[str]:
        """
        Compile a regex pattern for validating URLs based on the provided schemes.
        Args:
            schemes: Iterable of URL schemes to include in the regex.
        Returns:
            Compiled regex pattern for URL validation.
        """
        scheme_pattern = "|".join(schemes)
        return re.compile(
            rf"^({scheme_pattern}):\/\/[^./:\s][^/\s]+[^./:\s](\/.*)?$",
            re.IGNORECASE | re.UNICODE
        )

    def filter_value(self, value: str | None) -> str | None:
        """
        Convert the value to a Python string type.
        """
        value = str(value or "").strip()
        if not value:
            return ""

        if not self.rx_url.match(value):
            self.error = err.INVALID_URL
            return value

        scheme, domain, path, query, fragment = urlsplit(value)

        if ".." in domain:
            self.error = err.INVALID_URL
            return value

        try:
            domain = idna.uts46_remap(domain, std3_rules=False, transitional=False)
        except idna.IDNAError:  # pragma: no cover
            self.error = err.INVALID_URL
            return value

        scheme = scheme.lower()
        return urlunsplit((scheme, domain, path, query, fragment))

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        if not self.value:
            return True

        if self.one_of and self.value not in self.one_of:
            self.error = err.ONE_OF
            self.error_args = {"one_of": self.one_of}
            return False

        return True
