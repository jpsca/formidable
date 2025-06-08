"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import logging
import typing as t
from copy import copy

from . import errors as err
from .fields.base import Field
from .parser import parse
from .wrappers import ObjectManager


DELETED = "_deleted"

logger = logging.getLogger("formidable")


class Form():
    class Meta:
        # ORM class to use for creating new objects.
        orm_cls: t.Any = None

        # The class to use for wrapping objects in the form.
        obj_manager_cls: t.Type[ObjectManager] = ObjectManager

        # The primary key field of the objects in the form.
        pk: str = "id"

        # Custom messages for validation errors that expand/update the default ones to
        # customize or translate them. This argument should be a dictionary where keys
        # are error codes and values are human error messages.
        messages: dict[str, str]

        # Whether the form allows deletion of objects.
        # If set to True, the form will delete objects of form when the "_deleted"
        # field is present.
        allow_delete: bool = False

    _fields: dict[str, Field]
    _messages: dict[str, str]
    _object: ObjectManager
    _valid: bool | None = None
    _deleted: bool = False

    def __init__(
        self,
        reqdata: t.Any = None,
        object: t.Any = None,
        *,
        name_format: str = "{name}",
        messages: dict[str, str] | None = None,
    ):
        """

        Args:
            reqdata:
                The request data to parse and set the form fields. Defaults to `None`.
            object:
                An object to use as the source of the initial data for the form.
                Will be updates on `save()`. Defaults to `None`.
            name_format:
                A format string for the field names. Defaults to "{name}".
            messages:
                Custom messages for validation errors. Defaults to `None`, which uses the default messages.
                For `FormSet` and `FormField`, the messages set in the parent form ovewrride those set in
                the child forms.

        """

        self._set_meta()
        self._object = self.Meta.obj_manager_cls(self.Meta.orm_cls)
        self._set_messages(messages)

        self._fields = {}
        # Instead of regular dir(), that sorts by name
        for name in self.__dir__():
            if name.startswith("_"):
                continue
            field = getattr(self, name)
            if not isinstance(field, Field):
                continue

            # Clone the field to avoid modifying the original class attribute
            field = copy(field)
            setattr(self, name, field)

            field.parent = self
            field.field_name = name
            field.set_messages(self._messages)
            self._fields[name] = field

        self._set_name_format(name_format)
        if reqdata or object:
            self._set(parse(reqdata), object)

    def __repr__(self) -> str:
        attrs = []
        for name, field in self._fields.items():
            attrs.append(f"{name}={field.value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __iter__(self):
        return self._fields.values()

    def __contains__(self, name: str) -> bool:
        return name in self._fields

    @property
    def is_valid(self) -> bool:
        """
        Returns whether the form is valid.
        """
        if self._valid is None:
            return self.validate()
        return self._valid

    @property
    def is_invalid(self) -> bool:
        """
        Returns whether the form is invalid.
        """
        return not self.is_valid

    def get_errors(self) -> dict[str, str]:
        """
        Returns a dictionary of field names and their error messages.
        """
        errors = {}
        for name, field in self._fields.items():
            if field.error is not None:
                errors[name] = field.error
        return errors

    def validate(self) -> bool:
        """
        Returns whether the form is valid.
        """
        valid = True

        for field in self._fields.values():
            field.validate()
            if field.error is not None:
                valid = False

        valid = self.on_after_validation()

        self._valid = valid
        return valid

    def save(self) -> t.Any:
        if not self._deleted and not self.is_valid:
            raise ValueError("Form is not valid")

        if self._deleted:
            if self._object.exists():
                if not self.Meta.allow_delete:
                    logger.warning("Deletion is not allowed for this form %s", self)
                else:
                    return self._object.delete()
            return {DELETED: True}

        data = {}
        for name, field in self._fields.items():
            data[name] = field.save()

        if self._object.exists():
            return self._object.update(data)
        elif self._object.model_cls:
            return self._object.create(data)

        return data

    def on_after_validation(self) -> bool:
        """
        Hook method called after validation.
        Can be overridden to modify the field values or errors
        before saving.

        Returns:
            Whether the form is valid after the custom validation.

        """
        return True

    # Private methods

    def _set_meta(self):
        """
        Sets the Meta class attributes to the form instance.
        This is done to avoid modifying the original Meta class.
        """
        self.Meta = copy(self.Meta)

        orm_cls = getattr(self.Meta, "orm_cls", None)
        if (orm_cls is not None) and not isinstance(orm_cls, type):
            raise TypeError("Meta.orm_cls must be a class, not an instance.")
        self.Meta.orm_cls = orm_cls

        obj_manager_cls = getattr(self.Meta, "obj_manager_cls", ObjectManager)
        if not isinstance(obj_manager_cls, type):
            raise TypeError("Meta.obj_manager_cls must be a class, not an instance.")
        self.Meta.obj_manager_cls = obj_manager_cls

        messages = getattr(self.Meta, "messages", {})
        if not isinstance(messages, dict):
            raise TypeError("Meta.messages must be a dictionary.")
        self.Meta.messages = messages

        pk = getattr(self.Meta, "pk", "id")
        if not isinstance(pk, str):
            raise TypeError("Meta.pk must be a string.")
        self.Meta.pk = pk

        allow_delete = getattr(self.Meta, "allow_delete", False)
        if not isinstance(allow_delete, bool):
            raise TypeError("Meta.allow_delete must be a boolean.")
        self.Meta.allow_delete = allow_delete

    def _set_messages(self, messages: dict[str, str] | None = None):
        self._messages = {
            **err.MESSAGES,
            **self.Meta.messages,
            **(messages or {}),
        }

    def _set_name_format(self, name_format: str) -> None:
        for field in self._fields.values():
            field.set_name_format(name_format)

    def _set(self, reqdata: t.Any = None, object: t.Any = None) -> None:
        self._deleted = DELETED in reqdata if isinstance(reqdata, dict) else False
        if self._deleted:
            return

        self._valid = None

        reqdata = reqdata or {}
        self._object = self.Meta.obj_manager_cls(self.Meta.orm_cls, object)

        for name, field in self._fields.items():
            field.set(reqdata.get(name), self._object.get(name))
