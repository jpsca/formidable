"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_slug_field():
    class TestForm(f.Form):
        slug = f.SlugField()
        default_slug = f.SlugField(default="default-slug")

    form = TestForm({"slug": ["my-custom-slug"]})
    form.validate()
    print(form.get_errors())

    assert form.is_valid
    assert form.slug.value == "my-custom-slug"
    assert form.default_slug.value == "default-slug"

    data = form.save()
    print(data)
    assert data == {
        "slug": "my-custom-slug",
        "default_slug": "default-slug",
    }


def test_slug_field_invalid():
    class TestForm(f.Form):
        slug = f.SlugField()

    form = TestForm({"slug": ["Not a valid slug!"]})
    assert not form.is_valid
    assert form.slug.error == err.INVALID_SLUG

    form.slug.set("valid-slug_123")
    form.validate()
    assert form.slug.error is None
    assert form.is_valid


def test_validate_one_of():
    one_of = ["apple", "banana", "cherry"]
    field = f.SlugField(one_of=one_of, required=False)

    field.set("banana")
    field.validate()
    assert field.error is None

    field.set("orange")
    field.validate()
    assert field.error == err.ONE_OF
    assert field.error_args == {"one_of": one_of}


def test_invalid_one_of():
    with pytest.raises(ValueError):
        f.SlugField(one_of="not a list")  # type: ignore
