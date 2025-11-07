"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t


class ObjectManager:
    """
    A utility class for wrapping ORM objects and providing a consistent interface
    for creatimg, accessing atttributes, updating, and deleting objects.

    Args:
        object:
            The underlying data source. Can be a Multidict
            implementation or a regular dict.

    """

    def __init__(self, *, orm_cls: t.Any = None, object: t.Any = None):
        self.orm_cls = orm_cls
        self.object = None if object is None else object
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

        Args:
            data:
                A dictionary containing the data to save to the object.

        Returns:
            - If there is no wrapped object, and `orm_cls` is set, it creates
              a new instance and returns it.
            - If the wrapped object is an ORM model, calls `self.update()` to
              update its attributes and returns the updated object.
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
        Create a new instance of the model class with the provided data.

        Args:
            data:
                A dictionary containing the data to initialize the model.

        Returns:
            An instance of the model class initialized with the provided data.

        """
        assert self.orm_cls is not None
        if hasattr(self.orm_cls, "create"):
            return self.orm_cls.create(**data)
        return self.orm_cls(**data)

    def update(self, data: dict[str, t.Any]) -> t.Any:
        """
        Update an existing object with the provided data.

        Args:
            data:
                A dictionary containing the data to update the object with.

        Returns:
            The updated object.

        """
        assert self.object is not None
        for key, value in data.items():
            setattr(self.object, key, value)
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
