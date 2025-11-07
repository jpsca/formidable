"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""
import pytest

import formidable as f


@pytest.mark.parametrize("value", ["photo.jpg", ""])
def test_file_field(value):
    class TestForm(f.Form):
        photo = f.FileField(required=False)

    reqdata = {"photo": [value]}
    form = TestForm(reqdata)

    assert form.is_valid
    print(form.get_errors())
    assert form.photo.value == value

    data = form.save()
    print(data)
    assert data["photo"] == value


def test_empty_file_field_with_object_value():
    class TestForm(f.Form):
        photo = f.FileField()

    reqdata = {"photo": [""]}
    object = {"photo": "saved_photo.jpg"}
    form = TestForm(reqdata, object=object)

    assert form.is_valid
    print(form.get_errors())
    assert form.photo.value == object["photo"]

    data = form.save()
    print(data)
    assert data["photo"] == object["photo"]


def test_file_field_with_object_value():
    class TestForm(f.Form):
        photo = f.FileField()

    reqdata = {"photo": ["new_photo.jpg"]}
    object = {"photo": "saved_photo.jpg"}
    form = TestForm(reqdata, object=object)

    assert form.is_valid
    print(form.get_errors())
    assert form.photo.value == reqdata["photo"][0]

    data = form.save()
    print(data)
    assert data["photo"] == reqdata["photo"][0]


def test_file_field_required():
    class TestForm(f.Form):
        photo = f.FileField(required=True)

    reqdata = {"photo": [""]}
    form = TestForm(reqdata)

    assert form.is_invalid
    print(form.get_errors())
    assert form.photo.error == f.errors.REQUIRED

    form = TestForm({})

    assert form.is_invalid
    print(form.get_errors())
    assert form.photo.error == f.errors.REQUIRED
