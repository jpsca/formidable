"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_slug_field():
    class TestForm(f.Form):
        slug = f.SlugField()
        default_slug = f.SlugField(default="default-slug")

    form = TestForm({"slug": ["my-custom-slug"]})

    assert form.is_valid
    print(form.get_errors())
    assert form.slug.value == "my-custom-slug"
    assert form.default_slug.value == "default-slug"

    data = form.save()
    print(data)
    assert data == {
        "slug": "my-custom-slug",
        "default_slug": "default-slug",
    }


@pytest.mark.parametrize("input,expected", (
    ("This is a Test!", "this-is-a-test"),
    ("Café au lait", "cafe-au-lait"),
    ("100% Effective", "100-effective"),
    ("Hello, World!!!", "hello-world"),
    ("   Leading and trailing spaces   ", "leading-and-trailing-spaces"),
    ("Multiple    spaces", "multiple-spaces"),
    ("Special #$&* Characters", "special-characters"),
    ("Ünicöde Tëxt", "uenicoede-text"),
    ("Dashes - and underscores_", "dashes-and-underscores"),
    ("Nín hǎo. Wǒ shì zhōng guó rén", "nin-hao-wo-shi-zhong-guo-ren"),
    ("Привет мир", ""),  # Cyrillic characters removed
    ("مرحبا بالعالم", ""),  # Arabic characters removed
    ("שלום עולם", ""),  # Hebrew characters removed
    ("नमस्ते दुनिया", ""),  # Hindi characters removed
))
def test_slug_field_slugify(input, expected):
    field = f.SlugField()
    field.set(input)
    assert field.value == expected



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
