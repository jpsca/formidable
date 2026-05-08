"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

from unittest.mock import MagicMock

import pytest

import formidable as f


class PeeweeObject:
    """A mock Peewee ORM-like object for testing purposes."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.delete_instance = MagicMock(return_value=None)
        self.save = MagicMock(return_value=None)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class OtherObject:
    """A mock of a different ORM-like object for testing purposes."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.delete = MagicMock(return_value=None)


class SaveOnlyObject:
    """A mock ORM-like object with `save()` but no `create` classmethod —
    exercises the `Model(**data); obj.save()` fallback in ObjectManager.create.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.save = MagicMock(return_value=None)


@pytest.mark.parametrize("Object", [PeeweeObject, OtherObject])
def test_create_object(Object):
    class ProductForm(f.Form):
        class Meta:
            orm_cls = Object

        name = f.TextField()
        price = f.FloatField(gt=0)


    form = ProductForm({
        "name": ["Test Product"],
        "price": ["10.0"],
    })

    form.validate()
    assert form.is_valid
    obj = form.save()

    assert isinstance(obj, Object)
    assert obj.name == "Test Product"
    assert obj.price == 10.0


def test_update_object():
    class ProductForm(f.Form):
        name = f.TextField()
        price = f.FloatField(gt=0)


    existing_obj = PeeweeObject(name="Old Product", price=5.0)
    form = ProductForm(
        {
            "name": ["Updated Product"],
            "price": ["15.0"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()

    assert updated_obj is existing_obj
    assert updated_obj.name == "Updated Product"
    assert updated_obj.price == 15.0
    # Persistence is part of the contract: form.save() returns a fully-saved
    # object, not one waiting on a follow-up .save() call.
    existing_obj.save.assert_called_once()


def test_update_calls_save_when_available():
    """Regression: `form.save()` on an existing ORM object must invoke that
    object's `.save()` method so the consumer doesn't have to. Mirrors the
    behavior of `delete()` calling `delete_instance()` / `delete()`.
    """
    class ProductForm(f.Form):
        name = f.TextField()

    existing = PeeweeObject(name="Old")
    form = ProductForm({"name": ["New"]}, object=existing)
    assert form.is_valid

    form.save()

    existing.save.assert_called_once()


def test_update_skips_save_when_not_available():
    """An object without a `.save()` method (non-ORM dict-likes, mocks of
    custom domain objects) must still flow through update without errors.
    """
    class ProductForm(f.Form):
        name = f.TextField()

    existing = OtherObject(name="Old")  # no .save attribute
    form = ProductForm({"name": ["New"]}, object=existing)
    assert form.is_valid

    # Must not raise even though OtherObject doesn't have .save
    result = form.save()
    assert result is existing
    assert result.name == "New"


def test_create_fallback_persists_when_no_create_classmethod():
    """When the ORM class has no `create` classmethod, ObjectManager falls
    back to `Model(**data)` and then calls `obj.save()` if available, so
    the "create returns persisted instance" contract holds across ORMs that
    separate construction from persistence (SQLAlchemy detached, etc.).
    """
    class ProductForm(f.Form):
        class Meta:
            orm_cls = SaveOnlyObject
        name = f.TextField()

    form = ProductForm({"name": ["X"]})
    assert form.is_valid

    obj = form.save()

    assert isinstance(obj, SaveOnlyObject)
    assert obj.name == "X"
    obj.save.assert_called_once()


@pytest.mark.parametrize("Object", [PeeweeObject, OtherObject])
def test_delete_object(Object):
    class ChildForm(f.Form):
        class Meta:
            orm_cls = Object

        name = f.TextField()

    class ProductForm(f.Form):
        tags = f.NestedForms(ChildForm, allow_delete=True)

    tag1 = Object(id=3, name="cool")
    tag2 = Object(id=6, name="new")
    tag3 = Object(id=9, name="awesome")
    existing_obj = Object(name="Test Product", tags=[tag1, tag2, tag3])

    form = ProductForm(
        {
            "tags[3][name]": ["cool"],
            "tags[3][_id]": ["3"],

            "tags[6][_destroy]": ["1"],
            "tags[6][_id]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            "tags[9][_id]": ["9"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()

    if Object is PeeweeObject:
        tag2.delete_instance.assert_called_once()
    else:
        tag2.delete.assert_called_once_with()

    print(updated_obj.tags)
    assert updated_obj.tags == [tag1, tag3]


def test_delete_not_allowed():
    class ChildForm(f.Form):
        name = f.TextField()

    class ProductForm(f.Form):
        tags = f.NestedForms(ChildForm, allow_delete=False)

    tag1 = PeeweeObject(id=3, name="cool")
    tag2 = PeeweeObject(id=6, name="new")
    tag3 = PeeweeObject(id=9, name="awesome")
    existing_obj = PeeweeObject(name="Test Product", tags=[tag1, tag2, tag3])

    form = ProductForm(
        {
            "tags[3][name]": ["cool"],
            "tags[3][_id]": ["3"],

            "tags[6][_destroy]": ["1"],
            "tags[6][_id]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            "tags[9][_id]": ["9"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()

    tag2.delete_instance.assert_not_called()
    print(updated_obj.tags)
    assert updated_obj.tags == [tag1, tag2, tag3]


def test_empty_delete_field_is_no_delete():
    class ChildForm(f.Form):
        name = f.TextField()

    class ProductForm(f.Form):
        tags = f.NestedForms(ChildForm, allow_delete=False)

    tag1 = PeeweeObject(id=3, name="cool")
    tag2 = PeeweeObject(id=6, name="new")
    tag3 = PeeweeObject(id=9, name="awesome")
    existing_obj = PeeweeObject(name="Test Product", tags=[tag1, tag2, tag3])

    form = ProductForm(
        {
            "tags[3][name]": ["cool"],
            "tags[3][_id]": ["3"],

            "tags[6][_destroy]": [""],
            "tags[6][_id]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            "tags[9][_id]": ["9"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()

    tag2.delete_instance.assert_not_called()
    print(updated_obj.tags)
    assert updated_obj.tags == [tag1, tag2, tag3]


def test_delete_without_object():
    class ChildForm(f.Form):
        name = f.TextField()

    class ProductForm(f.Form):
        tags = f.NestedForms(ChildForm, allow_delete=True)

    existing_obj = PeeweeObject(name="Test Product", tags=[])

    form = ProductForm(
        {
            "tags[6][_destroy]": ["1"],
            "tags[6][_id]": ["6"],
            "tags[6][name]": ["meh"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()
    assert updated_obj.tags == []
