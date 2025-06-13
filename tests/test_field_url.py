"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_url_field():
    class TestForm(f.Form):
        website = f.URLField()
        default_url = f.URLField(default="http://example.com/path")

    form = TestForm({"website": ["https://formidable.dev"]})
    form.validate()
    print(form.get_errors())

    assert form.is_valid
    assert form.website.value == "https://formidable.dev"
    assert form.default_url.value == "http://example.com/path"

    data = form.save()
    print(data)
    assert data == {
        "website": "https://formidable.dev",
        "default_url": "http://example.com/path",
    }


def test_url_field_invalid():
    field = f.URLField()

    field.set("not a url")
    field.validate()
    assert field.error == err.INVALID_URL

    field.set("https://example.com")
    field.validate()
    assert field.error is None


def test_validate_one_of():
    one_of = ["http://a.com", "http://b.com", "http://b.com"]
    field = f.URLField(one_of=one_of, required=False)

    field.set("http://b.com")
    field.validate()
    assert field.error is None

    field.set("http://o.com")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": one_of}


def test_invalid_one_of():
    with pytest.raises(ValueError):
        f.URLField(one_of="not a list")  # type: ignore
