"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f
from formidable import errors as err


def test_form_field():
    class AddressForm(f.Form):
        street = f.TextField()
        city = f.TextField()

    class TestForm(f.Form):
        address = f.FormField(AddressForm)

    form = TestForm(
        {
            "address[street]": ["123 Main St"],
            "address[city]": ["Springfield"],
        }
    )

    assert form.address.form.street.name == "address[street]"  # type: ignore
    assert form.address.form.street.value == "123 Main St"  # type: ignore

    assert form.address.form.city.name == "address[city]"  # type: ignore
    assert form.address.form.city.value == "Springfield"  # type: ignore

    data = form.save()
    print(data)
    assert data == {
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
        }
    }


def test_form_field_object():
    class AddressForm(f.Form):
        street = f.TextField()
        city = f.TextField()

    class TestForm(f.Form):
        address = f.FormField(AddressForm)

    form = TestForm(
        object={
            "address": {
                "street": "123 Main St",
                "city": "Springfield",
            },
            "foo": "bar",
        }
    )

    assert form.address.form.street.name == "address[street]"  # type: ignore
    assert form.address.form.street.value == "123 Main St"  # type: ignore

    assert form.address.form.city.name == "address[city]"  # type: ignore
    assert form.address.form.city.value == "Springfield"  # type: ignore

    data = form.save()
    print(data)
    assert data == {
        "address": {
            "street": "123 Main St",
            "city": "Springfield",
        },
        "foo": "bar",
    }


def test_required():
    class AddressForm(f.Form):
        street = f.TextField(required=False)
        city = f.TextField(required=False)


    field = f.FormField(AddressForm)
    field.set(None)
    field.validate()
    assert field.error == err.REQUIRED
    assert field.error_message == err.MESSAGES[err.REQUIRED]

    field = f.FormField(AddressForm)
    field.set("")
    field.validate()
    assert field.error == err.REQUIRED

    field = f.FormField(AddressForm, required=False)
    field.set(None)
    field.validate()
    assert field.error is None
    assert field.error_message == ""


def test_default():
    class AddressForm(f.Form):
        street = f.TextField()
        city = f.TextField()

    def default_factory():
        return {
            "street": "123 Main St",
            "city": "Springfield",
        }

    class TestForm(f.Form):
        address = f.FormField(AddressForm, default=default_factory)

    form = TestForm({})

    assert form.is_valid
    print(form.address.error)
    data = form.save()
    print(data)
    assert data == {"address": default_factory()}
