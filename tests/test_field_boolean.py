"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f


def test_boolean_field():
    class TestForm(f.Form):
        alive = f.BooleanField(default=True)
        owner = f.BooleanField(default=False)
        admin = f.BooleanField()
        alien = f.BooleanField()
        meh = f.BooleanField(default=None)

    form = TestForm(
        {
            "admin": [""],
            "alien": ["false"],
            "owner": [55]
        }
    )

    assert form.alive.name == "alive"
    assert form.alive.value is True
    assert form.owner.value is True
    assert form.admin.value is True
    assert form.alien.value is False
    assert form.meh.value is False

    data = form.save()
    print(data)
    assert data == {
        "alive": True,
        "owner": True,
        "admin": True,
        "alien": False,
        "meh": False,
    }


def test_callable_default():
    class TestForm(f.Form):
        alive = f.BooleanField(default=lambda: True)

    form = TestForm()
    assert form.alive.value is True


def test_boolean_required():
    class TestForm(f.Form):
        agree = f.BooleanField(required=True)

    form = TestForm({})
    assert form.agree.error == f.errors.REQUIRED
    assert form.agree.value is False

