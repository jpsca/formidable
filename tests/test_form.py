"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f


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


def test_messages_inheritance_with_formset_field():
    MSG = "parent"

    class ChildForm(f.Form):
        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        myset = f.FormSet(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG


def test_messages_override_with_formset_field():
    MSG_PARENT = "parent"
    MSG_CHILD = "child"

    class ChildForm(f.Form):
        class Meta:
            messages = {"required": MSG_CHILD}

        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG_PARENT}

        myset = f.FormSet(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG_CHILD


def test_ignore_data_and_skip_validation_if_deleted():
    class TestForm(f.Form):
        name = f.TextField()
        age = f.IntegerField()

    form = TestForm({
        f.DELETED: "1",
        "age": ["whatever"],
    })

    assert form.validate() is True

    data = form.save()
    print(data)
    assert data == {f.DELETED: True}

