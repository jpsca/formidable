"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f


def test_html_attribute_escaping():
    field = f.TextField(required=False)
    field.field_name = "test"
    field.value = 'hello" onclick="alert(1)'

    result = str(field.text_input())
    # The quote should be escaped, not raw
    assert 'value="hello&#34; onclick=&#34;alert(1)"' in result
    assert 'value="hello" onclick="alert(1)"' not in result


def test_label():
    field = f.TextField()
    field.field_name = "test"

    # Test with default text
    result = field.label()
    assert result == f'<label for="{field.id}">Test</label>'

    # Test with custom text
    result = field.label("Custom Label")
    assert result == f'<label for="{field.id}">Custom Label</label>'

    # Test with custom attributes
    result = field.label("Label", class_="custom-class")
    assert result == f'<label for="{field.id}" class="custom-class">Label</label>'


def test_label_default_text_replaces_underscores():
    field = f.TextField()
    field.field_name = "first_name"

    assert field.label() == f'<label for="{field.id}">First name</label>'


def test_label_text_from_field_definition():
    field = f.TextField(label="My input")
    field.field_name = "test"

    assert field.label_text == "My input"
    assert field.label() == f'<label for="{field.id}">My input</label>'

    # An explicit text takes precedence
    result = field.label("Custom Label")
    assert result == f'<label for="{field.id}">Custom Label</label>'

    # An empty text is not replaced by the generated one
    field = f.TextField(label="")
    field.field_name = "test"
    assert field.label() == f'<label for="{field.id}"></label>'


def test_label_text_is_escaped():
    field = f.TextField(label="<b>Name</b>")

    assert field.label() == f'<label for="{field.id}">&lt;b&gt;Name&lt;/b&gt;</label>'


def test_label_text_is_none_by_default():
    assert f.TextField().label_text is None


def test_label_text_in_form():
    class MyForm(f.Form):
        my_input = f.TextField(label="My input", required=False)
        other = f.TextField(required=False)

    form = MyForm()

    assert form.my_input.label_text == "My input"
    assert form.my_input.label() == f'<label for="{form.my_input.id}">My input</label>'
    assert form.other.label_text is None


class ChildForm(f.Form):
    name = f.TextField(required=False)


@pytest.mark.parametrize(
    "field",
    [
        f.BooleanField(label="Lorem"),
        f.DateField(label="Lorem"),
        f.DateTimeField(label="Lorem"),
        f.EmailField(label="Lorem"),
        f.FileField(label="Lorem"),
        f.FloatField(label="Lorem"),
        f.FormField(ChildForm, label="Lorem"),
        f.IntegerField(label="Lorem"),
        f.JSONField(label="Lorem"),
        f.ListField(label="Lorem"),
        f.NestedForms(ChildForm, label="Lorem"),
        f.SlugField(label="Lorem"),
        f.TextField(label="Lorem"),
        f.TimeField(label="Lorem"),
        f.URLField(label="Lorem"),
    ],
    ids=lambda field: field.__class__.__name__,
)
def test_all_fields_accept_label(field):
    assert field.label_text == "Lorem"


def test_error_tag():
    field = f.TextField(messages={
        "test_error": "This is a test error",
        "html_error": "This is an<br> error with HTML",
    })

    # Test with no error
    result = field.error_tag()
    assert result == ""

    # Test with error
    field.error = "test_error"
    result = field.error_tag()
    assert result == f'<div id="{field.id}-error" class="field-error">This is a test error</div>'

    # Test with custom attributes
    result = field.error_tag(class_="custom-error", test=True)
    expected = f'<div id="{field.id}-error" class="custom-error" test>This is a test error</div>'
    assert result == expected

    # Test with HTML
    field.error = "html_error"
    result = field.error_tag()
    assert result == f'<div id="{field.id}-error" class="field-error">This is an<br> error with HTML</div>'


def test_text_input():
    field = f.TextField()
    field.field_name = "test"
    field.value = "test value"

    result = field.text_input()
    expected = f'<input type="text" id="{field.id}" name="test" value="test value" required />'
    assert result == expected

    # Test with custom attributes
    result = field.text_input(class_="custom-class")
    assert 'class="custom-class"' in result


def test_text_input_not_required():
    field = f.TextField(required=False)
    field.field_name = "test"

    result = field.text_input()
    assert "required" not in result


def test_text_input_error():
    field = f.TextField(required=False)
    field.field_name = "test"
    field.error = "invalid"

    result = field.text_input()
    expected = (
        f'<input type="text" id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


def test_textarea():
    field = f.TextField()
    field.field_name = "test"
    field.value = "test value"

    result = field.textarea()
    expected = f'<textarea id="{field.id}" name="test" required>test value</textarea>'
    assert result == expected

    # Test with custom attributes
    result = field.textarea(rows="5", cols="40")
    assert 'rows="5"' in result
    assert 'cols="40"' in result


def test_textarea_not_required():
    field = f.TextField(required=False)
    field.field_name = "test"

    result = field.textarea()
    assert "required" not in result


def test_textarea_error():
    field = f.TextField(required=False)
    field.field_name = "test"
    field.error = "invalid"

    result = field.textarea()
    expected = (
        f'<textarea id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error"></textarea>'
    )
    assert result == expected


def test_select():
    field = f.TextField()
    field.field_name = "test"
    field.value = "2"

    options = [("1", "One"), ("2", "Two"), ("3", "Three")]
    result = field.select(options)
    expected = (
        f'<select id="{field.id}" name="test" required>\n'
        f'<option value="1">One</option>\n'
        f'<option value="2" selected>Two</option>\n'
        f'<option value="3">Three</option>\n'
        f'</select>'
    )
    assert result == expected

    # Test with custom attributes
    result = field.select(options, class_="custom-class")
    assert 'class="custom-class"' in result


def test_select_multiple():
    field = f.ListField()
    field.field_name = "test"
    field.value = ["2", "3"]

    options = [("1", "One"), ("2", "Two"), ("3", "Three")]
    result = field.select(options)
    expected = (
        f'<select id="{field.id}" name="test" multiple required>\n'
        f'<option value="1">One</option>\n'
        f'<option value="2" selected>Two</option>\n'
        f'<option value="3" selected>Three</option>\n'
        f'</select>'
    )
    assert result == expected


def test_select_not_required():
    field = f.TextField(required=False)
    field.field_name = "test"

    options = [("1", "One"), ("2", "Two"), ("3", "Three")]
    result = field.select(options)
    assert "required" not in result


def test_select_error():
    field = f.TextField(required=False)
    field.field_name = "test"
    field.error = "invalid"

    options = [("1", "One"), ("2", "Two"), ("3", "Three")]
    result = field.select(options)
    expected = (
        f'<select id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error">\n'
        f'<option value="1">One</option>\n'
        f'<option value="2">Two</option>\n'
        f'<option value="3">Three</option>\n'
        f'</select>'
    )
    assert result == expected


def test_checkbox():
    field = f.BooleanField()
    field.field_name = "test"

    hidden = '<input type="hidden" name="test" value="0" />'

    # Test unchecked
    field.value = False
    result = field.checkbox()
    expected = f'{hidden}<input type="checkbox" id="{field.id}" name="test" />'
    assert result == expected

    # Test checked
    field.value = True
    result = field.checkbox()
    expected = f'{hidden}<input type="checkbox" id="{field.id}" name="test" checked />'
    assert result == expected
    assert field.checkbox_input() == expected


def test_checkbox_of_a_field_that_is_not_boolean():
    field = f.TextField()
    field.field_name = "test"
    field.value = "x"

    result = field.checkbox()
    expected = f'<input type="checkbox" id="{field.id}" name="test" checked />'
    assert result == expected


def test_checkbox_disabled():
    """A disabled checkbox sends nothing, and its value must not change."""
    field = f.BooleanField()
    field.field_name = "test"
    field.value = True

    result = field.checkbox(disabled=True)
    expected = f'<input type="checkbox" id="{field.id}" name="test" checked disabled />'
    assert result == expected


def test_checkbox_of_another_form():
    field = f.BooleanField()
    field.field_name = "test"

    result = field.checkbox(form="other")
    expected = (
        '<input type="hidden" name="test" value="0" form="other" />'
        f'<input type="checkbox" id="{field.id}" name="test" form="other" />'
    )
    assert result == expected


def test_checkbox_error():
    field = f.BooleanField()
    field.field_name = "test"
    field.error = "invalid"

    result = field.checkbox()
    expected = (
        '<input type="hidden" name="test" value="0" />'
        f'<input type="checkbox" id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


def test_radio():
    field = f.TextField()
    field.field_name = "test"

    # Test with value not matching
    result = field.radio("option1")
    expected = f'<input type="radio" id="{field.id}" name="test" value="option1" />'
    assert result == expected

    # Test with matching value
    field.value = "option1"
    result = field.radio("option1")
    expected = f'<input type="radio" id="{field.id}" name="test" value="option1" checked />'
    assert result == expected


def test_radio_error():
    field = f.TextField()
    field.field_name = "test"
    field.error = "invalid"

    result = field.radio("option1")
    expected = (
        f'<input type="radio" id="{field.id}" name="test" value="option1"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


def test_file_input():
    field = f.FileField()
    field.field_name = "test"

    result = field.file_input()
    expected = f'<input type="file" id="{field.id}" name="test" required />'
    assert result == expected


def test_file_input_error():
    field = f.FileField(required=False)
    field.field_name = "test"
    field.error = "invalid"

    result = field.file_input()
    expected = (
        f'<input type="file" id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


def test_hidden_input():
    field = f.TextField()
    field.field_name = "test"
    field.value = "test value"

    result = field.hidden_input()
    expected = '<input type="hidden" name="test" value="test value" />'
    assert result == expected


def test_password_input():
    field = f.TextField()
    field.field_name = "test"
    field.value = "test value"

    result = field.password_input()
    expected = f'<input type="password" id="{field.id}" name="test" value="test value" required />'
    assert result == expected

    # Overwrite value
    result = field.password_input(value="")
    expected = f'<input type="password" id="{field.id}" name="test" value="" required />'
    assert result == expected


def test_password_error():
    field = f.TextField(required=False)
    field.field_name = "test"
    field.error = "invalid"

    result = field.password_input()
    expected = (
        f'<input type="password" id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


@pytest.mark.parametrize("method_name,input_type", [
    ("color_input", "color"),
    ("date_input", "date"),
    ("datetime_input", "datetime-local"),
    ("email_input", "email"),
    ("month_input", "month"),
    ("number_input", "number"),
    ("range_input", "range"),
    ("search_input", "search"),
    ("tel_input", "tel"),
    ("time_input", "time"),
    ("url_input", "url"),
    ("week_input", "week"),
])
def test_special_inputs(method_name, input_type):
    """Test all the special input types"""
    field = f.TextField()
    field.field_name = "test"
    field.value = "test value"
    method = getattr(field, method_name)

    result = method()
    expected = f'<input type="{input_type}" id="{field.id}" name="test" value="test value" required />'
    assert result == expected

    # Test with custom attributes
    result = method(class_="custom-class")
    assert 'class="custom-class"' in result


@pytest.mark.parametrize("method_name,input_type", [
    ("color_input", "color"),
    ("date_input", "date"),
    ("datetime_input", "datetime-local"),
    ("email_input", "email"),
    ("month_input", "month"),
    ("number_input", "number"),
    ("range_input", "range"),
    ("search_input", "search"),
    ("tel_input", "tel"),
    ("time_input", "time"),
    ("url_input", "url"),
    ("week_input", "week"),
])
def test_special_inputs_error(method_name, input_type):
    """Test all the special input types"""
    field = f.TextField(required=False)
    field.field_name = "test"
    field.error = "invalid"
    method = getattr(field, method_name)

    result = method()
    expected = (
        f'<input type="{input_type}" id="{field.id}" name="test"'
        f' aria-invalid="true" aria-errormessage="{field.id}-error" />'
    )
    assert result == expected


def test_isoformat_value_rendering():
    """Test that fields with isoformat values render correctly."""
    import datetime

    field = f.DateField(required=False)
    field.field_name = "birthday"
    field.value = datetime.date(2025, 3, 9)

    result = field.date_input()
    assert 'value="2025-03-09"' in result
