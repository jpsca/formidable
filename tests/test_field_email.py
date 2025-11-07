"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_email_field():
    class TestForm(f.Form):
        email = f.EmailField()
        default_email = f.EmailField(default="aaa@example.com")

    form = TestForm({"email": ["hello@jpscaletti.com"]})

    assert form.is_valid
    print(form.get_errors())
    assert form.email.value == "hello@jpscaletti.com"
    assert form.default_email.value == "aaa@example.com"

    data = form.save()
    print(data)
    assert data == {
        "email": "hello@jpscaletti.com",
        "default_email": "aaa@example.com",
    }


@pytest.mark.parametrize(
    "email",
    [
        "banana@example.com",
        " banana@example.com  ",  # spaces around email
        "banana@mail.example.com",  # subdomain
        "steve.jobs@apple.com",  # dots in local part
        "steve.jobs+spam@gmail.com",  # plus sign in local part
    ],
)
def test_valid_emails(email):
    field = f.EmailField()
    field.set(email)

    assert field.error is None
    assert field.value == email.strip()


def test_email_field_invalid():
    class TestForm(f.Form):
        email = f.EmailField()

    form = TestForm({"email": ["not an email"]})
    assert form.is_invalid
    assert form.email.error == err.INVALID_EMAIL


def test_validate_one_of():
    one_of = ["apple@example.com", "banana@example.com", "cherry@example.com"]
    field = f.EmailField(one_of=one_of, required=False)

    field.set("banana@example.com")
    field.validate()
    assert field.error is None

    field.set("orange@example.com")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": one_of}


def test_invalid_one_of():
    with pytest.raises(ValueError):
        f.EmailField(one_of="not a list")  # type: ignore
