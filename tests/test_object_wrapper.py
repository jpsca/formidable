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

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class OtherObject:
    """A mock of a different ORM-like object for testing purposes."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.delete = MagicMock(return_value=None)


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
    assert obj.name == "Test Product"  # type: ignore
    assert obj.price == 10.0  # type: ignore


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


@pytest.mark.parametrize("Object", [PeeweeObject, OtherObject])
def test_delete_object(Object):
    class ChildForm(f.Form):
        class Meta:
            orm_cls = Object

        name = f.TextField()

    class ProductForm(f.Form):
        tags = f.NestedForms(ChildForm)

    tag1 = Object(id=3, name="cool")
    tag2 = Object(id=6, name="new")
    tag3 = Object(id=9, name="awesome")
    existing_obj = Object(name="Test Product", tags=[tag1, tag2, tag3])

    form = ProductForm(
        {
            "tags[3][name]": ["cool"],
            f"tags[3][{f.PK_NAME}]": ["3"],

            f"tags[6][{f.DELETED_NAME}]": ["1"],
            f"tags[6][{f.PK_NAME}]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            f"tags[9][{f.PK_NAME}]": ["9"],
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
            f"tags[3][{f.PK_NAME}]": ["3"],

            f"tags[6][{f.DELETED_NAME}]": ["1"],
            f"tags[6][{f.PK_NAME}]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            f"tags[9][{f.PK_NAME}]": ["9"],
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
            f"tags[3][{f.PK_NAME}]": ["3"],

            f"tags[6][{f.DELETED_NAME}]": [""],
            f"tags[6][{f.PK_NAME}]": ["6"],
            "tags[6][name]": ["meh"],

            "tags[9][name]": ["awesome"],
            f"tags[9][{f.PK_NAME}]": ["9"],
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
        tags = f.NestedForms(ChildForm)

    existing_obj = PeeweeObject(name="Test Product", tags=[])

    form = ProductForm(
        {
            f"tags[6][{f.DELETED_NAME}]": ["1"],
            f"tags[6][{f.PK_NAME}]": ["6"],
            "tags[6][name]": ["meh"],
        },
        object=existing_obj
    )

    form.validate()
    assert form.is_valid
    updated_obj = form.save()
    assert updated_obj.tags == []
