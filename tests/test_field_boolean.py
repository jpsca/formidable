"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
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


def test_before_hook():
    """
    Test that the before hook is called before setting the value.
    """
    def before_hook(value):
        return not value


    class TestForm(f.Form):
        cat_alive = f.BooleanField(before=[before_hook])


    form = TestForm({"cat_alive": "1"})
    assert form.cat_alive.value is False


def test_before_hook_error():
    """
    Test that ValueError raised in before hook is handled correctly.
    """
    def before_hook(value):
        raise ValueError("Error in before hook", {"foo": "bar"})

    class TestForm(f.Form):
        cat_alive = f.BooleanField(before=[before_hook])


    form = TestForm({})
    assert form.cat_alive.error == "Error in before hook"
    assert form.cat_alive.error_args == {"foo": "bar"}
