"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from markupsafe import Markup

from .. import errors as err
from .base import Field


class BooleanField(Field):
    """
    A field that represents a boolean value.

    Boolean fields are treated specially because of how browsers handle checkboxes:

    - If not checked: the browser doesn't send the field at all.
    - If checked: It sends the "value" attribute, but this is optional, so it could
        send an empty string instead.

    For these reasons:

    - A string value in the `FALSE_VALUES` tuple (case-insensitive) will become `False`.
    - Any other value, including an empty string, will become `True`.
    - A missing field keeps the value of the object, if the form has one. Without
        an object, it takes the default value of the field, and `False` if there
        is none.

    So a missing field cannot be told apart from an unchecked checkbox, and with
    an object whose value is `True`, the checkbox could never be unchecked. To
    solve it, `checkbox()` renders a hidden input before the checkbox, with the
    same name and the value `"0"`: an unchecked checkbox then sends `"0"`, and
    a checked one sends both values, of which the last one is used.
    If you write the HTML of the checkbox yourself, add that hidden input too.

    Args:
        required:
            Whether the field value *must* be `True`. Defaults to `False`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        label:
            Text of the field's label, stored as `label_text`. Used by the
            `label()` render method when it is called without a text.
            Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    FALSE_VALUES = ("false", "0", "no")

    def __init__(
        self,
        *,
        required: bool = False,
        default: t.Any = None,
        label: str | None = None,
        messages: dict[str, str] | None = None,
    ):
        super().__init__(
            required=required,
            default=default,
            label=label,
            messages=messages,
        )

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None
        self._error = None
        self._error_args = None

        value = objvalue if reqvalue is None else reqvalue
        if value is None:
            value = self.default_value

        try:
            value = self._custom_filter(value)
        except ValueError as e:
            self._error = e.args[0] if e.args else err.INVALID
            self._error_args = e.args[1] if len(e.args) > 1 else None
            return

        self.value = self.filter_value(value)

        if self.required and not self.value:
            self._error = err.REQUIRED

    def filter_value(self, value: str | bool | None) -> bool:
        """
        Convert the value to a Python boolean type.
        """
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            value = value.lower().strip()
            if value in self.FALSE_VALUES:
                return False
        return True


    def checkbox(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="checkbox">` element, preceded
        by a hidden input with the same name and the value `"0"`, so unchecking
        it is sent as a false value instead of as nothing.

        The hidden input is left out when the checkbox is `disabled`: a disabled
        checkbox sends nothing, and the value of the field must not change.

        Args:
            **attrs:
                Additional HTML attributes to include in the checkbox input element.

        Example:
            ```pycon
            >>> import formidable as f
            >>> field = f.BooleanField()

            >>> print(field.checkbox())
            <input type="hidden" name="field_name" value="0" /><input type="checkbox" id="f-123abc" name="field_name" />
            ```

        """
        checkbox = super().checkbox(**attrs)
        if attrs.get("disabled"):
            return checkbox
        hidden_attrs = {"type": "hidden", "name": self.name, "value": "0"}
        if "form" in attrs:
            hidden_attrs["form"] = attrs["form"]
        hidden = Markup(f"<input {self._render_html_attrs(hidden_attrs)} />")
        return hidden + checkbox

    checkbox_input = checkbox  # Alias


BoolField = BooleanField  # Alias
