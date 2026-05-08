"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t


class ObjectManager:
    """
    A utility class for wrapping ORM objects and providing a consistent interface
    for creating, accessing attributes, updating, and deleting objects.

    Args:
        object:
            The underlying data source. Can be a Multidict
            implementation or a regular dict.

    """

    def __init__(self, *, orm_cls: t.Any = None, object: t.Any = None):
        self.orm_cls = orm_cls
        self.object = object
        self.is_dict = (object is not None) and isinstance(object, dict)

    def exists(self) -> bool:
        """Check if the wrapped object exists."""
        return self.object is not None

    def get(self, name: str, default: t.Any = None) -> t.Any:
        if self.object is None:
            return default
        if self.is_dict:
            return self.object.get(name, default)
        return getattr(self.object, name, default)

    def save(self, data: dict[str, t.Any]) -> t.Any:
        """
        Save the provided data to the wrapped object.

        For ORM-bound forms (whether creating a new instance or updating an
        existing one) the returned object is fully persisted: `create()`
        relies on the ORM's own `create` classmethod (which inserts) or
        falls back to `Model(**data); obj.save()`; `update()` does setattrs
        and then calls `obj.save()`. Consumers don't need a follow-up
        `instance.save()` call.

        Args:
            data:
                A dictionary containing the data to save to the object.

        Returns:
            - If there is no wrapped object, and `orm_cls` is set, it creates
              and persists a new instance and returns it.
            - If the wrapped object is an ORM model, calls `self.update()` to
              update its attributes, persists, and returns the updated object.
            - If the wrapped object is a dictionary, it updates the dictionary
              with the new data and returns the updated dictionary.
            - Otherwise, it just returns the new data.

        """
        if self.object is None and self.orm_cls is not None:
            return self.create(data)
        elif self.object is not None:
            if self.is_dict:
                return {**self.object, **data}
            else:
                return self.update(data)
        else:
            return data

    def create(self, data: dict[str, t.Any]) -> t.Any:
        """
        Create and persist a new instance of the model class with the
        provided data.

        Uses the ORM's `create` classmethod when available (the peewee
        idiom — instantiates and INSERTs in one call). Otherwise falls
        back to `Model(**data)` and then calls `obj.save()` if the
        instance has one, so the contract "create returns a persisted
        instance" holds across ORMs that separate construction from
        persistence (e.g. SQLAlchemy detached instances).

        Args:
            data:
                A dictionary containing the data to initialize the model.

        Returns:
            A persisted instance of the model class initialized with the
            provided data.

        """
        assert self.orm_cls is not None
        if hasattr(self.orm_cls, "create"):
            return self.orm_cls.create(**data)
        obj = self.orm_cls(**data)
        if hasattr(obj, "save"):
            obj.save()
        return obj

    def update(self, data: dict[str, t.Any]) -> t.Any:
        """
        Update an existing object with the provided data and persist it.

        Setattrs each entry of `data` onto `self.object`, then calls
        `obj.save()` if available. The `hasattr` guard mirrors the pattern
        used in `delete()` so non-ORM objects (which lack a `save` method)
        flow through unchanged.

        Args:
            data:
                A dictionary containing the data to update the object with.

        Returns:
            The persisted, updated object.

        """
        assert self.object is not None
        for key, value in data.items():
            setattr(self.object, key, value)
        if hasattr(self.object, "save"):
            self.object.save()
        return self.object

    def delete(self) -> t.Any:
        """
        Delete the provided object.

        Returns:
            The result of the deletion operation, which may vary based on the ORM used.

        """
        assert self.object is not None
        if hasattr(self.object, "delete_instance"):
            return self.object.delete_instance()
        return self.object.delete()
