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
from .wrappers import ObjectWrapper


DELETED = "_deleted"

logger = logging.getLogger("formidable")


class Form:
    class Meta:
        # ORM class to use for creating new objects.
        orm_cls: t.Any = None

        # The primary key field of the objects in the form.
        pk: str = "id"

        # Messages for validation errors. This should be a dictionary where keys are
        # error codes and values are human error messages.
        # This can be used to customize/translate error messages for the form fields.
        # If not provided, the default `formidable.errors.MESSAGES` will be used.
        messages: dict[str, str]

        # Whether the form allows deletion of objects.
        # If set to True, the form will delete objects of form when the "_deleted"
        # field is present.
        allow_delete: bool = False

    _fields: dict[str, Field]
    _object: ObjectWrapper | None = None
    _valid: bool | None = None
    _deleted: bool = False

    def __init__(
        self,
        reqdata: t.Any = None,
        object: t.Any = None,
        *,
        name_format: str = "{name}",
    ):
        """
        """

        # Clone the metadata class to avoid modifying the original attribute
        self.meta = copy(self.Meta)
        self._set_messages()

        fields = {}
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
            field.set_messages(self.Meta.messages)
            fields[name] = field

        self._fields = fields
        self._set_name_format(name_format)

        if reqdata or object:
            self._set(parse(reqdata), object)

    def __repr__(self):
        attrs = []
        for name, field in self._fields.items():
            attrs.append(f"{name}={field.value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __iter__(self):
        return self._fields.values()

    def __contains__(self, name):
        return name in self._fields

    def _set_messages(self, messages: dict[str, str] | None = None):
        self.Meta.messages = messages or getattr(self.Meta, "messages", err.MESSAGES)

    def _set_name_format(self, name_format: str):
        for field in self._fields.values():
            field.set_name_format(name_format)

    def _set(self, reqdata: t.Any = None, object: t.Any = None):
        self._deleted = DELETED in reqdata if isinstance(reqdata, dict) else False
        if self._deleted:
            return

        self._valid = False
        reqdata = reqdata or {}
        self._object = wr_object = ObjectWrapper(object)
        for name, field in self._fields.items():
            field.set(reqdata.get(name), wr_object.get(name))

    def get_errors(self) -> dict[str, str]:
        """
        Returns a dictionary of field names and their error messages.
        """
        errors = {}
        for name, field in self._fields.items():
            if field.error is not None:
                errors[name] = field.error
        return errors

    def is_valid(self) -> bool:
        """
        Returns whether the form is valid.
        """
        if self._valid is None:
            return self.validate()
        return self._valid

    def validate(self) -> bool:
        """
        Returns whether the form is valid.
        """
        valid = True
        for field in self._fields.values():
            field.validate()
            if field.error is not None:
                valid = False

        self._valid = valid
        return valid

    def save(self) -> t.Any:
        if not self._deleted and not self.is_valid:
            raise ValueError("Form is not valid")

        if self._deleted:
            if self._object:
                if not self.Meta.allow_delete:
                    logger.warning("Deletion is not allowed for this form %s", self)
                else:
                    return self._object.delete()
            return {DELETED: True}

        data = {}
        for name, field in self._fields.items():
            data[name] = field.save()

        if self._object:
            return self._object.update(data)

        if self.Meta.orm_cls:
            return self.Meta.orm_cls(**data)

        return data
