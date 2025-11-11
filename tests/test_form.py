"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f


def test_reserved_words():
    for name in f.RESERVED_NAMES:
        with pytest.raises(ValueError):
            class TestForm(f.Form):
                locals()[name] = f.TextField()

            TestForm()


def test_contains():
    class TestForm(f.Form):
        a = f.TextField()
        b = f.TextField()
        c = f.TextField()

    form = TestForm()

    assert "a" in form
    assert list(form) == [form.a, form.b, form.c]


def test_no_errors():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({"name": "John"})
    form.validate()

    assert form.is_valid
    assert form.name.error is None
    assert form.get_errors() == {}


def test_errors():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.is_invalid
    assert form.name.error == "required"
    assert form.get_errors() == {"name": "required"}


def test_save_invalid_form():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({})

    with pytest.raises(ValueError):
        form.save()


def test_invalid_orm_cls():
    class TestForm(f.Form):
        class Meta:
            orm_cls = "lol"

        name = f.TextField()

    with pytest.raises(ValueError):
        TestForm()


def test_invalid_custom_messages():
    class TestForm(f.Form):
        class Meta:
            messages = "lol"

        name = f.TextField()

    with pytest.raises(ValueError):
        TestForm()


def test_invalid_custom_pk():
    class TestForm(f.Form):
        class Meta:
            pk = None

        name = f.TextField()

    with pytest.raises(ValueError):
        TestForm()


def test_custom_messages():
    MSG = "Custom required message in Meta"

    class TestForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.name.error == "required"
    assert form.name.error_message == MSG


def test_field_messages():
    MSG = "Custom required message in field"

    class TestForm(f.Form):
        name1 = f.TextField(messages={"required": MSG})
        name2 = f.TextField()

    form = TestForm({})
    form.validate()
    assert form.name1.error == "required"
    assert form.name2.error == "required"
    assert form.name1.error_message == MSG
    assert form.name2.error_message != MSG


def test_field_messages_overrides_form_messages():
    MSG_FORM = "Form required message"
    MSG_FIELD = "Field required message"

    class TestForm(f.Form):
        class Meta:
            messages = {"required": MSG_FORM}

        name1 = f.TextField(messages={"required": MSG_FIELD})
        name2 = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.name1.error == "required"
    assert form.name1.error_message == MSG_FIELD
    assert form.name2.error == "required"
    assert form.name2.error_message == MSG_FORM


def test_messages_inheritance_with_form_field():
    MSG = "parent"

    class ChildForm(f.Form):
        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        ff = f.FormField(ChildForm)

    form = ParentForm({"ff[name]": ""})
    form.validate()

    assert form.ff.form.name.error == "required"  # type: ignore
    assert form.ff.form.name.error_message == MSG  # type: ignore


def test_messages_override_with_form_field():
    MSG_PARENT = "parent"
    MSG_CHILD = "child"

    class ChildForm(f.Form):
        class Meta:
            messages = {"required": MSG_CHILD}

        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG_PARENT}

        ff = f.FormField(ChildForm)

    form = ParentForm({"ff[name]": ""})
    form.validate()

    assert form.ff.form.name.error == "required"  # type: ignore
    assert form.ff.form.name.error_message == MSG_CHILD  # type: ignore


def test_messages_inheritance_with_nested_field():
    MSG = "parent"

    class ChildForm(f.Form):
        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        myset = f.NestedForms(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG


def test_messages_override_with_nested_field():
    MSG_PARENT = "parent"
    MSG_CHILD = "child"

    class ChildForm(f.Form):
        class Meta:
            messages = {"required": MSG_CHILD}

        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG_PARENT}

        myset = f.NestedForms(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG_CHILD


def test_custom_filter():
    class TestForm(f.Form):
        name = f.TextField(required=False)

        def filter_name(self, value):
            return value.upper()

    form = TestForm({"name": "Zoe"})
    assert form.is_valid
    assert form.name.value == "ZOE"


def test_custom_filter_with_error():
    class TestForm(f.Form):
        name = f.TextField(required=False)

        def filter_name(self, value):
            if value and value.startswith("Z"):
                raise ValueError("no-z-names")
            return value

    form = TestForm({"name": "Zoe"})
    assert form.is_invalid
    assert form.name.error == "no-z-names"

    form = TestForm({})
    assert form.is_valid


def test_custom_validator():
    class TestForm(f.Form):
        name = f.TextField()

        def validate_name(self, value):
            return value.upper()

    form = TestForm({"name": "Zoe"})
    assert form.is_valid
    assert form.name.value == "ZOE"


def test_custom_validator_with_error():
    class TestForm(f.Form):
        name = f.TextField()

        def validate_name(self, value):
            if value.startswith("Z"):
                raise ValueError("no-z-names")
            return value

    form = TestForm({"name": "Zoe"})
    assert form.is_invalid
    assert form.name.error == "no-z-names"


def test_boolean_custom_filter_with_error():
    class TestForm(f.Form):
        bool = f.BooleanField()

        def filter_bool(self, value):
            if value == "maybe":
                raise ValueError("not-an-answer")
            return value

    form = TestForm({"bool": "maybe"})
    assert form.is_invalid


def test_file_custom_filter_with_error():
    class TestForm(f.Form):
        photo = f.FileField()

        def filter_photo(self, value):
            raise ValueError("you-shall-not-pass")

    form = TestForm({"photo": "test.jpg"})
    assert form.is_invalid


def test_form_validation():
    class TestForm(f.Form):
        password1 = f.TextField()
        password2 = f.TextField()

        def after_validate(self):
            if self.password1.value != self.password2.value:
                self.password2.error = "invalid"
                return False
            return True

    form = TestForm({"password1": "abc", "password2": "abc"})
    assert form.is_valid

    form = TestForm({"password1": "abc", "password2": "def"})
    assert form.is_invalid


def test_hidden_tags():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm()
    expected = f'<input type="hidden" name="{f.DELETED_NAME}" />'
    assert str(form.hidden_tags) == expected


def test_hidden_tags_with_pk():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm(object={"id": 42})
    expected = (
        f'<input type="hidden" name="{f.DELETED_NAME}" />\n'
        f'<input type="hidden" name="{f.PK_NAME}" value="42" />'
    )
    assert str(form.hidden_tags) == expected


def test_hidden_tags_fake_object():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm(object={"name": "meh"})
    expected = f'<input type="hidden" name="{f.DELETED_NAME}" />'
    assert str(form.hidden_tags) == expected
