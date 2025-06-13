"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f
from formidable import errors as err


def test_email_field():
    class TestForm(f.Form):
        email = f.EmailField()
        default_email = f.EmailField(default="aaa@example.com")

    form = TestForm({"email": ["hello@jpscaletti.com"]})
    form.validate()
    print(form.get_errors())

    assert form.is_valid
    assert form.email.value == "hello@jpscaletti.com"
    assert form.default_email.value == "aaa@example.com"

    data = form.save()
    print(data)
    assert data == {
        "email": "hello@jpscaletti.com",
        "default_email": "aaa@example.com",
    }


def test_email_field_invalid():
    class TestForm(f.Form):
        email = f.EmailField()

    form = TestForm({"email": ["not an email"]})
    assert not form.is_valid
    assert form.email.error == err.INVALID_EMAIL
