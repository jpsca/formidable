"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f


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


def test_error_tag():
    field = f.TextField(messages={"test_error": "This is a test error"})

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

    # Test unchecked
    field.value = False
    result = field.checkbox()
    expected = f'<input type="checkbox" id="{field.id}" name="test" />'
    assert result == expected

    # Test checked
    field.value = True
    result = field.checkbox()
    expected = f'<input type="checkbox" id="{field.id}" name="test" checked />'
    assert result == expected


def test_checkbox_error():
    field = f.BooleanField()
    field.field_name = "test"
    field.error = "invalid"

    result = field.checkbox()
    expected = (
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
