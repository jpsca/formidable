"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import formidable as f


def test_ignore_data_and_skip_validation_if_deleted():
    class TestForm(f.Form):
        name = f.TextField()
        age = f.IntegerField()

    form = TestForm({
        f.DELETED: "1",
        "age": ["whatever"],
    })

    assert form.validate() is True

    data = form.save()
    print(data)
    assert data == {f.DELETED: True}

