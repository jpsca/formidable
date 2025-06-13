"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable


try:
    from email_validator import validate_email
except ImportError:
    validate_email = None

from formidable import errors as err

from .base import Field, TCustomValidator


class EmailField(Field):
    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        check_dns: bool = False,
        allow_smtputf8: bool = False,
        before: Iterable[TCustomValidator] | None = None,
        after: Iterable[TCustomValidator] | None = None,
        one_of: Iterable[str] | None = None,
        messages: dict[str, str] | None = None,
    ):
        """
        A field for normalizing and validating email addresses.

        Uses the "JoshData/python-email-validator" library for the normalization, which includes:

        - Lowercasing the domain part of the email address, because domain names are case-insensitive.
        - Unicode "NFC" normalization of the whole address, which turns characters plus combining
          characters into precomposed characters where possible and replaces certain Unicode
          characters (such as angstrom and ohm) with other equivalent code points
          (a-with-ring and omega), replacement of fullwidth and halfwidth characters in the domain
          part, and possibly other UTS46 mappings on the domain part.

        Args:
            required:
                Whether the field is required. Defaults to `True`.
            default:
                Default value for the field. Defaults to `None`.
            check_dns:
                If `True`, DNS queries are made to check that the domain name in the email
                address (the part after the @-sign) can receive mail. Defaults to `False`.
            allow_smtputf8:
                Accept non-ASCII characters in the local part of the address
                (before the @-sign). These email addresses require that your mail
                submission library and the mail servers along the route to the destination,
                including your own outbound mail server, all support the
                [SMTPUTF8 (RFC 6531)](https://tools.ietf.org/html/rfc6531) extension.
                By default this is set to `False`.
            before:
                List of custom validators to run before setting the value.
            after:
                List of custom validators to run after setting the value.
            one_of:
                List of values that the field value must be one of. Defaults to `None`.
            messages:
                Overrides of the error messages, specifically for this field.

        """
        self.check_dns = check_dns
        self.allow_smtputf8 = allow_smtputf8

        if one_of is not None:
            if isinstance(one_of, str) or not isinstance(one_of, Iterable):
                raise ValueError("`one_of` must be an iterable (but not a string) or `None`")
        self.one_of = one_of

        default = str(default) if default is not None else None

        super().__init__(
            required=required,
            default=default,
            before=before,
            after=after,
            messages=messages,
        )

    def to_python(self, value: str | None) -> str | None:
        """
        Convert the value to a Python string type.
        """
        value = str(value or "").strip()
        if not value:
            return ""

        if validate_email is None:
            raise ImportError(
                "The 'email_validator' package is required for EmailField. "
                "Please install it with 'pip install email_validator'."
            )
        try:
            validated = validate_email(
                value,
                check_deliverability=self.check_dns,
                allow_smtputf8=self.allow_smtputf8,
            )
            return validated.normalized
        except (ValueError, TypeError):
            self.error = err.INVALID_EMAIL
        return value

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
