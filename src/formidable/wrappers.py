"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t


class ObjectManager:
    def __init__(self, model_cls: t.Any = None, object: t.Any = None):
        """
        A utility class for wrapping ORM objects and providing a consistent interface
        for creatimg, accessing atttributes, updating, and deleting objects.

        Args:
            object:
                The underlying data source. Can be a Multidict
                implementation or a regular dict.

        """
        self.model_cls = model_cls
        self.object = None if object is None else object
        self.is_dict = isinstance(self.object, dict)

    def __bool__(self) -> bool:
        """Check if the wrapped object exists."""
        return self.object is None

    def exists(self) -> bool:
        """Check if the wrapped object exists."""
        return self.object is not None

    def get(self, name: str, default: t.Any = None) -> t.Any:
        if self.object is None:
            return default
        if self.is_dict:
            return self.object.get(name, default)
        return getattr(self.object, name, default)

    def create(self, data: dict[str, t.Any]) -> t.Any:
        """
        Create a new instance of the model class with the provided data.

        Args:
            model_cls:
                The class of the model to create.
            data:
                A dictionary containing the data to initialize the model.

        Returns:
            An instance of the model class initialized with the provided data.

        """
        assert self.model_cls is not None
        return self.model_cls.create(**data)

    def update(self, data: dict[str, t.Any]) -> t.Any:
        """
        Update an existing object with the provided data.

        Args:
            object:
                The object to update.
            data:
                A dictionary containing the data to update the object with.

        Returns:
            The updated object.

        """
        assert self.object is not None
        if self.is_dict:
            self.object.update(data)
        else:
            for key, value in data.items():
                setattr(self.object, key, value)
        return self.object

    def delete(self) -> t.Any:
        """
        Delete the provided object.

        Args:
            object:
                The object to delete.

        Returns:
            The result of the deletion operation, which may vary based on the ORM used.

        """
        assert self.object is not None
        if self.is_dict:
            return self.object.clear()
        else:
            return self.object.delete_instance()
