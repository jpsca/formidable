"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f
from formidable import errors as err


def test_nested_field():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.NestedForms(SkillForm)

    form = TestForm(
        {
            "skills[0][name]": ["Python"],
            "skills[0][level]": ["5"],
            "skills[1][name]": ["JavaScript"],
            "skills[1][level]": ["3"],
        }
    )


    assert form.skills.empty_form.name.name == "skills[NEW_RECORD][name]"  # type: ignore
    assert form.skills.empty_form.level.name == "skills[NEW_RECORD][level]"  # type: ignore

    assert form.skills.forms[0].name.name == "skills[0][name]"
    assert form.skills.forms[0].name.value == "Python"

    assert form.skills.forms[0].level.name == "skills[0][level]"
    assert form.skills.forms[0].level.value == 5

    assert form.skills.forms[1].name.name == "skills[1][name]"
    assert form.skills.forms[1].name.value == "JavaScript"

    assert form.skills.forms[1].level.name == "skills[1][level]"
    assert form.skills.forms[1].level.value == 3

    data = form.save()
    print(data)
    assert data == {
        "skills": [
            {"name": "Python", "level": 5},
            {"name": "JavaScript", "level": 3},
        ]
    }


def test_empty_initi():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.NestedForms(SkillForm)

    form = TestForm()
    form.skills.set(None, [{}, {}])
    assert len(form.skills.forms) == 2


def test_nested_field_object():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.NestedForms(SkillForm)

    form = TestForm(
        object={
            "skills": [
                {"id": 5, "name": "Python", "level": 5},
                {"id": 7, "name": "JavaScript", "level": 3},
            ]
        }
    )

    assert form.skills.empty_form.name.name == "skills[NEW_RECORD][name]"  # type: ignore
    assert form.skills.empty_form.level.name == "skills[NEW_RECORD][level]"  # type: ignore

    assert form.skills.forms[0].name.name == "skills[0][name]"
    assert form.skills.forms[0].name.value == "Python"

    assert form.skills.forms[0].level.name == "skills[0][level]"
    assert form.skills.forms[0].level.value == 5

    assert form.skills.forms[0].hidden_tags == (
        f'<input type="hidden" name="skills[0][{f.DELETED_NAME}]" />\n'
        f'<input type="hidden" name="skills[0][{f.PK_NAME}]" value="5" />'
    )

    assert form.skills.forms[1].name.name == "skills[1][name]"
    assert form.skills.forms[1].name.value == "JavaScript"

    assert form.skills.forms[1].level.name == "skills[1][level]"
    assert form.skills.forms[1].level.value == 3

    assert form.skills.forms[1].hidden_tags == (
        f'<input type="hidden" name="skills[1][{f.DELETED_NAME}]" />\n'
        f'<input type="hidden" name="skills[1][{f.PK_NAME}]" value="7" />'
    )


def test_nested_field_object_updated():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.NestedForms(SkillForm)

    form = TestForm(
        {
            "skills[0][name]": ["Go"],
            "skills[0][level]": ["2"],
            f"skills[0][{f.PK_NAME}]": ["7"],
        },
        object={
            "skills": [
                {"id": 5, "name": "Python", "level": 5},
                {"id": 7, "name": "JavaScript", "level": 3},
            ]
        }
    )

    assert form.skills.empty_form.name.name == "skills[NEW_RECORD][name]"  # type: ignore
    assert form.skills.empty_form.level.name == "skills[NEW_RECORD][level]"  # type: ignore

    assert form.skills.forms[0].name.name == "skills[0][name]"
    assert form.skills.forms[0].name.value == "Go"

    assert form.skills.forms[0].level.name == "skills[0][level]"
    assert form.skills.forms[0].level.value == 2

    assert form.skills.forms[1].name.name == "skills[1][name]"
    assert form.skills.forms[1].name.value == "Python"

    assert form.skills.forms[1].level.name == "skills[1][level]"
    assert form.skills.forms[1].level.value == 5

    data = form.save()
    print(data)
    assert data == {
        "skills": [
            {"id": 7, "name": "Go", "level": 2},
            {"id": 5, "name": "Python", "level": 5},
        ]
    }


class ChildForm(f.Form):
    meh = f.TextField(required=False)


def test_empty_nested():
    class TestForm(f.Form):
        items = f.NestedForms(ChildForm)

    form = TestForm()
    data = form.save()
    print(data)
    assert data == {"items": []}


def test_subforms_with_errors():
    class ChildForm(f.Form):
        meh = f.TextField(required=True)

    field = f.NestedForms(ChildForm)
    field.set({
        "0": {"meh": ""},
        "1": {"meh": "Hello"},
        "2": {},
    })

    field.validate()
    print(field.error_args)
    assert field.error == err.INVALID
    assert field.error_args == {
        0: {"meh": err.REQUIRED},
        2: {"meh": err.REQUIRED},
    }


def test_validate_min_items():
    field = f.NestedForms(ChildForm, min_items=3)

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
    })
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}

    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
    })
    field.validate()
    assert field.error is None


def test_validate_mixed_min_items():
    field = f.NestedForms(ChildForm, min_items=3)

    # One new and one existing = 2
    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
        ]
    )
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}

    # One new and two existing = 3
    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
        ],
    )
    field.validate()
    assert field.error is None

    # One update (id=1) and one existing = 2
    field.set(
        {
            "0": {f.PK_NAME: 1, "meh": "1"},  # update object
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
        ],
    )
    field.validate()
    assert field.error == err.MIN_ITEMS
    assert field.error_args == {"min_items": 3}


def test_invalid_min_items():
    with pytest.raises(ValueError):
        f.NestedForms(ChildForm, min_items="not an int")  # type: ignore


def test_validate_max_items():
    field = f.NestedForms(ChildForm, max_items=3)

    # Four new items
    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
        "3": {"meh": "4"},
    })
    field.validate()
    assert field.error == err.MAX_ITEMS
    assert field.error_args == {"max_items": 3}

    # Three new items
    field.set({
        "0": {"meh": "1"},
        "1": {"meh": "2"},
        "2": {"meh": "3"},
    })
    field.validate()
    assert field.error is None

    field.set({})
    field.validate()
    assert field.error is None


def test_validate_mixed_max_items():
    field = f.NestedForms(ChildForm, max_items=3)

    field.set({})
    field.validate()
    assert field.error is None

    # One new and three existing = 4
    field.set(
        {
            "0": {"meh": "1"},
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error == err.MAX_ITEMS
    assert field.error_args == {"max_items": 3}

    # One update and two existing = 3
    field.set(
        {
            "0": {f.PK_NAME: 1, "meh": "1"},  # update object
        },
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error is None

    # Three existing
    field.set(
        {},
        [
            {"id": 1, "meh": "2"},
            {"id": 2, "meh": "3"},
            {"id": 3, "meh": "4"},
        ],
    )
    field.validate()
    assert field.error is None


def test_invalid_max_items():
    with pytest.raises(ValueError):
        f.NestedForms(ChildForm, max_items="not an int")  # type: ignore


def test_nested_build():
    class SkillForm(f.Form):
        name = f.TextField()
        level = f.IntegerField(default=1)

    class TestForm(f.Form):
        skills = f.NestedForms(SkillForm)

    form = TestForm()
    form.skills.build(num=3)

    assert len(form.skills.forms) == 3
    assert form.skills.forms[0].name.error is None
    assert form.skills.forms[0].level.error is None
    assert form.skills.forms[1].name.error is None
    assert form.skills.forms[1].level.error is None
    assert form.skills.forms[2].name.error is None
    assert form.skills.forms[2].level.error is None
