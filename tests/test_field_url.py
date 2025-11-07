"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_url_field():
    class TestForm(f.Form):
        website = f.URLField()
        default_url = f.URLField(default="http://example.com/path")

    form = TestForm({"website": ["https://formidable.dev"]})

    assert form.is_valid
    print(form.get_errors())
    assert form.website.value == "https://formidable.dev"
    assert form.default_url.value == "http://example.com/path"

    data = form.save()
    print(data)
    assert data == {
        "website": "https://formidable.dev",
        "default_url": "http://example.com/path",
    }


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com",
        " https://example.com ",  # spaces around URL
        "http://example.com/path/to/resource",
        "https://example.com/path/to/resource?query=param#fragment",
        "https://subdomain.example.com",
        "http://example.co.uk",
        "http://xn--eckwd4c7c.xn--zckzah",  # Punycode example
        "http://example.com:8080",  # With port
        "https://127.0.0.1/path",  # IPv4 address
        "https://[2001:db8::1]/path",  # IPv6 address
        "https://localhost",
    ],
)
def test_valid_urls(url):
    field = f.URLField()
    field.set(url)

    assert field.error is None
    assert field.value == url.strip()


def test_normalize_url():
    field = f.URLField()

    field.set("HTTP://EXAMPLE.COM/PATH")
    assert field.error is None
    assert field.value == "http://example.com/PATH"

    field.set("http://example.com/Some⒈Path")
    assert field.error is None
    assert field.value == "http://example.com/Some⒈Path"

    field.set("http://example．com/path")
    assert field.error is None
    assert field.value == "http://example.com/path"


def test_not_an_url():
    field = f.URLField()

    field.set("not a url")
    assert field.error == err.INVALID_URL


def test_space_in_url():
    field = f.URLField()

    field.set("http://ex ample.com/path")
    assert field.error == err.INVALID_URL

    field.set("http://example.com/some path")
    assert field.error is None


def test_two_dots_in_domain():
    field = f.URLField()

    field.set("http://example..com")
    assert field.error == err.INVALID_URL


def test_invalid_character():
    field = f.URLField()
    field.set("http://exampl⒈e.com/abcdef")
    assert field.error == err.INVALID_URL


def test_invalid_scheme():
    field = f.URLField(schemes=["http", "https"])

    field.set("ftp://example.com")
    assert field.error == err.INVALID_URL


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
