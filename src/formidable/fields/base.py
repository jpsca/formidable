"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable
from uuid import uuid4

from markupsafe import Markup

from .. import errors as err


if t.TYPE_CHECKING:
    from ..form import Form


class Field:
    """
    Base class for all form fields.

    Args:
        required:
            Whether the field is required. Defaults to `True`.
        default:
            Default value for the field. Can be a static value or a callable.
            Defaults to `None`.
        messages:
            Dictionary of error codes to custom error message templates.
            These override the default error messages for this specific field.
            Example: {"required": "This field cannot be empty"}.

    """

    parent: "Form | None" = None
    name_format: str = "{name}"
    field_name: str = ""
    default: t.Any = None
    value: t.Any = None
    error: str | dict[str, t.Any] | None = None
    error_args: dict[str, t.Any] | None = None
    messages: dict[str, str]
    default_render_method: str = "text_input"

    # Whether the value of this field is a list of values.
    multiple: bool = False

    def __init__(
        self,
        *,
        required: bool = True,
        default: t.Any = None,
        messages: dict[str, str] | None = None,
    ):
        self.required = required
        self.default = default
        self.value = self.default_value
        self.messages = messages if messages is not None else {}
        self.id = f"f-{uuid4().hex}"

    def __repr__(self):
        attrs = [
            f"name={self.name!r}",
            f"value={self.value!r}",
            f"default={self.default!r}",
            f"error={self.error!r}",
        ]
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    @property
    def name(self) -> str:
        return self.name_format.format(name=self.field_name)

    @property
    def error_message(self) -> str:
        """
        Returns the error message for the field, if any, using the field's error
        template and arguments. Returns an empty string if there is no error.
        """
        if self.error is None or not isinstance(self.error, str):
            return ""
        tmpl = self.messages.get(self.error, err.MESSAGES.get(self.error, self.error))
        args = self.error_args or {}
        return tmpl.format(**args)

    @property
    def default_value(self) -> t.Any:
        """
        Calculates the default value of the field, if default is a callable.
        """
        if callable(self.default):
            return self.default()
        return self.default

    def set_messages(self, messages: dict[str, str]):
        self.messages = {**messages, **self.messages}

    def set_name_format(self, name_format: str):
        self.name_format = name_format

    def set(self, reqvalue: t.Any, objvalue: t.Any = None):
        self.error = None
        self.error_args = None

        value = objvalue if reqvalue is None else reqvalue
        if value is None:
            value = self.default_value

        try:
            value = self._custom_filter(value)
        except ValueError as e:
            self.error = e.args[0] if e.args else err.INVALID
            self.error_args = e.args[1] if len(e.args) > 1 else None
            return

        self.value = value
        if self.required and value in [None, ""]:
            self.error = err.REQUIRED
            return

        try:
            self.value = self.filter_value(value)
        except (ValueError, TypeError):
            self.error = err.INVALID
            return

    def filter_value(self, value: t.Any) -> t.Any:
        """
        Convert the value to the appropriate Python type for this field.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.filter_value() must be implemented"
        )

    def validate(self) -> bool:
        """
        Validates the field's current value using both built-in and custom validators.

        Returns:
            bool: True if validation passes, False if any validation fails.

        """
        if self.error is not None:
            return False

        self.validate_value()

        if self.error:
            return False

        try:
            self.value = self._custom_validator(self.value)
        except ValueError as e:
            self.error = e.args[0] if e.args else err.INVALID
            self.error_args = e.args[1] if len(e.args) > 1 else None
            return False

        return True

    def validate_value(self) -> bool:
        """
        Performs field-specific validation on the current value.
        Can be overridden by subclasses to add custom validation logic.

        Returns:
            bool: True if validation passes, False otherwise.

        """
        return True

    def save(self) -> t.Any:
        return self.value

    def _custom_filter(self, value: t.Any) -> t.Any:
        return value

    def _custom_validator(self, value: t.Any) -> t.Any:
        return value

    # Helper methods for rendering HTML forms

    def render(self, label: str | None = None, method: str | None = None, **attrs: t.Any) -> str:
        """
        A shortcut method to call the label, input, and error_tag rendering methods
        in one go.

        Args:
            label:
                The text to display inside the label.
                If `None`, is not included
            method:
                The rendering method to use (e.g., "text_input", "textarea").
            **attrs:
                Additional HTML attributes to include in the rendered input element.

        """
        label_html = self.label(label) if label else ""

        method = method or self.default_render_method
        render_method = getattr(self, method, None)
        if not callable(render_method):
            raise ValueError(f"Invalid render method: {method}")
        field_html = render_method(**attrs)

        error_html = self.error_tag()

        return Markup(f"{label_html}\n{field_html}\n{error_html}".strip())

    def label(self, text: str | None = None, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<label>` element. Adds a `for` attribute
        pointing to the field's ID.

        Args:
            text:
                The text to display inside the label. If `None`, uses the field's name.
            **attrs:
                Additional HTML attributes to include in the label element.

        """
        attributes = {
            "for": self.id,
            **attrs,
        }
        attr_str = self._render_html_attrs(attributes)
        label_text = text if text is not None else self.field_name.capitalize()
        return Markup(f"<label {attr_str}>{label_text}</label>")

    def error_tag(self, *, tag: str = "span", **attrs: t.Any) -> str:
        """
        If the field has an error, renders the field's error message as an
        HTML element. Default tag is `<span>`.

        Args:
            tag:
                The HTML tag to use for the error message. Defaults to "span".
            **attrs:
                Additional HTML attributes to include in the error element.

        """
        if self.error is None:
            return Markup("")

        tag = tag.lower()
        attributes = {
            "id": f"{self.id}-error",
            "class": "field-error",
            **attrs,
        }
        attr_str = self._render_html_attrs(attributes)
        return Markup(f"<{tag} {attr_str}>{self.error_message}</{tag}>")

    def text_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="text">` element.

        Args:
            **attrs:
                Additional HTML attributes to include in the text input element.

        """
        return self._input(input_type="text", **attrs)

    def textarea(
        self,
        **attrs: t.Any,
    ) -> str:
        """
        Renders the field as an HTML `<textarea>` element.

        Args:
            **attrs:
                Additional HTML attributes to include in the textarea element.

        """
        attributes = {
            "id": self.id,
            "name": self.name,
            "required": self.required,
        }
        if self.error:
            attributes["aria-invalid"] = "true"
            attributes["aria-errormessage"] = f"{self.id}-error"
        attributes.update(attrs)
        attr_str = self._render_html_attrs(attributes)

        value_str = "" if self.value is None else str(self.value)
        return Markup(f"<textarea {attr_str}>{value_str}</textarea>")

    def select(
        self,
        options: Iterable[tuple[str, str]],
        **attrs: t.Any,
    ) -> str:
        """
        Renders the field as an HTML `<select>` element. If the field supports multiple
        selections, the `multiple` attribute will be added automatically.

        Args:
            options:
                A list of tuples representing the options for the select element.
                Each tuple should contain the option value and display text.
                If the field's value matches an option's value, that option will be
                rendered as selected.
            **attrs:
                Additional HTML attributes to include in the select element.

        """
        attributes = {
            "id": self.id,
            "name": self.name,
            "multiple": self.multiple,
            "required": self.required,
        }
        if self.error:
            attributes["aria-invalid"] = "true"
            attributes["aria-errormessage"] = f"{self.id}-error"
        attributes.update(attrs)
        attr_str = self._render_html_attrs(attributes)

        options_html = ""
        values = map(str, self.value) if self.multiple else [str(self.value)]

        for value, display in options:
            selected_attr = " selected" if str(value) in values else ""
            options_html += f'<option value="{value}"{selected_attr}>{display}</option>\n'

        return Markup(f"<select {attr_str}>\n{options_html}</select>")

    def checkbox(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="checkbox">` element.

        A check box allowing single values to be selected/deselected.
        If the field's value is truthy, the checkbox will be rendered as checked.

        Args:
            **attrs:
                Additional HTML attributes to include in the checkbox input element.

        """
        attributes = {
            "type": "checkbox",
            "id": self.id,
            "name": self.name,
            "checked": bool(self.value),
        }
        if self.error:
            attributes["aria-invalid"] = "true"
            attributes["aria-errormessage"] = f"{self.id}-error"
        attributes.update(attrs)
        attr_str = self._render_html_attrs(attributes)
        return Markup(f"<input {attr_str} />")

    checkbox_input = checkbox  # Alias

    def radio(self, radio_value: str, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="radio">` element.

        A radio button, allowing a single value to be selected out of
        multiple choices with the same name value.

        Args:
            radio_value:
                The value attribute for this radio button. If it matches the field's value,
                the radio button will be rendered as checked.
            **attrs:
                Additional HTML attributes to include in the radio input element.

        """
        attributes = {
            "type": "radio",
            "id": self.id,
            "name": self.name,
            "value": radio_value,
            "checked": str(self.value) == str(radio_value),
        }
        if self.error:
            attributes["aria-invalid"] = "true"
            attributes["aria-errormessage"] = f"{self.id}-error"
        attributes.update(attrs)
        attr_str = self._render_html_attrs(attributes)
        return Markup(f"<input {attr_str} />")

    radio_input = radio  # Alias

    def _input(self, input_type: str = "text", **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input>` element.

        Args:
            input_type:
                The type of the input element (e.g., "text", "email", "number").
                Defaults to "text".
            **attrs:
                Additional HTML attributes to include in the input element.

        """
        attributes = {
            "type": input_type,
            "id": self.id,
            "name": self.name,
            "value": "" if self.value is None else str(self.value),
            "required": self.required,
        }
        if self.error:
            attributes["aria-invalid"] = "true"
            attributes["aria-errormessage"] = f"{self.id}-error"
        attributes.update(attrs)
        attr_str = self._render_html_attrs(attributes)
        return Markup(f"<input {attr_str} />")

    def file_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="file">` element.

        This is a control that lets the user select a file. Use the `accept` attribute
        to define the types of files that the control can select.

        Args:
            **attrs:
                Additional HTML attributes to include in the file input element.

        """
        return self._input(input_type="file", **attrs)

    def hidden_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="hidden">` element.

        This is a control that is not displayed but whose value is submitted to the server.

        Args:
            **attrs:
                Additional HTML attributes to include in the hidden input element.

        """
        attributes = {
            "type": "hidden",
            "name": self.name,
            "value": "" if self.value is None else str(self.value),
            **attrs,
        }
        attr_str = self._render_html_attrs(attributes)
        return Markup(f"<input {attr_str} />")

    def password_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="password">` element.

        A single-line text input whose value is obscured.
        Will alert user if site is not secure.

        Args:
            **attrs:
                Additional HTML attributes to include in the password input element.

        """
        return self._input(input_type="password", **attrs)

    def color_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="color">` element.

        This is a control for specifying a color.
        Opens a color picker when active in supporting browsers.

        Args:
            **attrs:
                Additional HTML attributes to include in the color input element.

        """
        return self._input(input_type="color", **attrs)

    def date_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="date">` element.

        This is a control for entering a date (year, month, and day, with no time).
        Opens a date picker or numeric wheels for year, month, and day when active in supporting browsers.
        active in supporting browsers.

        Args:
            **attrs:
                Additional HTML attributes to include in the date input element.

        """
        return self._input(input_type="date", **attrs)

    def datetime_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="datetime-local">` element.

        This is a control for entering a date and time, with no time zone.
        Opens a date picker or numeric wheels for date- and time-components when
        active in supporting browsers.

        Args:
            **attrs:
                Additional HTML attributes to include in the datetime input element.

        """
        return self._input(input_type="datetime-local", **attrs)

    def email_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="email">` element.

        This is a control for editing an email address. Looks like a text input,
        but has relevant keyboard in supporting browsers and devices
        with dynamic keyboards.

        Args:
            **attrs:
                Additional HTML attributes to include in the email input element.

        """
        return self._input(input_type="email", **attrs)

    def month_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="month">` element.

        This is a control for entering a month and year, with no time zone.

        Args:
            **attrs:
                Additional HTML attributes to include in the month input element.

        """
        return self._input(input_type="month", **attrs)

    def number_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="number">` element.

        This is a control for entering a number. Displays a spinner and adds default validation.
        Displays a numeric keypad in some devices with dynamic keypads.

        Args:
            **attrs:
                Additional HTML attributes to include in the number input element.

        """
        return self._input(input_type="number", **attrs)

    def range_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="range">` element.

        This is a control for entering a number whose exact value is not important.

        Displays as a range widget defaulting to the middle value. Used in conjunction
        `min` and `max` to define the range of acceptable values.

        Args:
            **attrs:
                Additional HTML attributes to include in the range input element.

        """
        return self._input(input_type="range", **attrs)

    def search_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="search">` element.

        A single-line text input for entering search strings.
        Line-breaks are automatically removed from the input value.
        May include a delete icon in supporting browsers that
        can be used to clear the field.

        Displays a search icon instead of enter key on some devices with dynamic keypads.

        Args:
            **attrs:
                Additional HTML attributes to include in the search input element.

        """
        return self._input(input_type="search", **attrs)

    def tel_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="tel">` element.

        This is a control for entering a telephone number. Displays a telephone keypad
        in some devices with dynamic keypads.

        Args:
            **attrs:
                Additional HTML attributes to include in the tel input element.

        """
        return self._input(input_type="tel", **attrs)

    def time_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="time">` element.

        This is a control for entering a time value with no time zone.

        Args:
            **attrs:
                Additional HTML attributes to include in the time input element.

        """
        return self._input(input_type="time", **attrs)

    def url_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="url">` element.

        This is a control entering a URL. Looks like a text input, but has
        relevant keyboard in supporting browsers and devices with dynamic keyboards.

        Args:
            **attrs:
                Additional HTML attributes to include in the url input element.

        """
        return self._input(input_type="url", **attrs)

    def week_input(self, **attrs: t.Any) -> str:
        """
        Renders the field as an HTML `<input type="week">` element.

        This is a control for entering a date consisting of a week-year number
        and a week number with no time zone.

        Args:
            **attrs:
                Additional HTML attributes to include in the week input element.

        """
        return self._input(input_type="week", **attrs)

    def _render_html_attrs(self, attrs: dict[str, t.Any]) -> str:
        """
        Renders HTML attributes from a dictionary.

        Args:
            **attrs:
                A dictionary of HTML attributes to render.

        """
        html_props = []
        clean_attrs = {}
        for key, value in attrs.items():
            if key == "class_":
                key = "class"
            key = key.replace("_", "-")
            if isinstance(value, bool):
                if value:
                    html_props.append(key)
            else:
                clean_attrs[key] = value

        html_attrs = [f'{key}="{value}"' for key, value in clean_attrs.items()]

        return " ".join(html_attrs + html_props)
