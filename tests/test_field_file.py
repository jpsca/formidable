"""
Formable | Copyright (c) 2025 Juan-Pablo Scaletti
"""
import pytest

import formidable as f


@pytest.mark.parametrize("value", ["photo.jpg", ""])
def test_file_field(value):
    class TestForm(f.Form):
        photo = f.FileField()

    reqdata = {"photo": [value]}
    form = TestForm(reqdata)
    form.validate()
    print(form.get_errors())

    assert form.is_valid
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
    form.validate()
    print(form.get_errors())

    assert form.is_valid
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
    form.validate()
    print(form.get_errors())

    assert form.is_valid
    assert form.photo.value == reqdata["photo"][0]

    data = form.save()
    print(data)
    assert data["photo"] == reqdata["photo"][0]
