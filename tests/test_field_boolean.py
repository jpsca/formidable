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
    assert form.is_invalid
    assert form.agree.error == f.errors.REQUIRED
    assert form.agree.value is False


class _Settings:
    def __init__(self, notify):
        self.notify = notify


def test_checkbox_of_an_object_can_be_unchecked():
    class TestForm(f.Form):
        notify = f.BooleanField()

    # What a browser sends for the output of `checkbox()`: the hidden input
    # and, only if it is checked, the checkbox.
    unchecked = {"notify": ["0"]}
    checked = {"notify": ["0", "on"]}

    form = TestForm(unchecked, _Settings(notify=True))
    assert form.notify.value is False
    assert form.save().notify is False

    form = TestForm(checked, _Settings(notify=False))
    assert form.notify.value is True
    assert form.save().notify is True


def test_missing_field_keeps_the_value_of_the_object():
    """e.g. an API client that only sends the fields it wants to change."""
    class TestForm(f.Form):
        name = f.TextField(required=False)
        notify = f.BooleanField()

    form = TestForm({"name": ["x"]}, _Settings(notify=True))
    assert form.notify.value is True

    form = TestForm({"name": ["x"]}, _Settings(notify=False))
    assert form.notify.value is False
