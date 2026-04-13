"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f


class SignInForm(f.Form):
    login = f.TextField()
    password = f.TextField()


def test_set_does_not_expose_error_until_validate():
    form = SignInForm({"foo": "bar"})

    assert form.login.error is None
    assert form.password.error is None
    assert form.login._error == "required"
    assert form.password._error == "required"

    assert form.is_valid is False

    assert form.login.error == "required"
    assert form.password.error == "required"
