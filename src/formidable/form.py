"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import logging
import typing as t
from copy import copy

from .fields.base import Field
from .fields.text import TextField
from .parser import parse
from .wrappers import ObjectManager


# Instead of "_delete", we use "_destroy" to be compatible with Rails forms.
DELETED = "_destroy"

logger = logging.getLogger("formidable")


class DefaultMeta:
    # ORM class to use for creating new objects.
    orm_cls: t.Any = None

    # The primary key field of the objects in the form.
    pk: str = "id"

    # Custom messages for validation errors that expand/update the default ones to
    # customize or translate them. This argument should be a dictionary where keys
    # are error codes and values are human error messages.
    messages: dict[str, str]


class Form():
    # The class to use for wrapping objects in the form.
    _ObjectManager: t.Type[ObjectManager] = ObjectManager

    _messages: dict[str, str]
    _name_format: str = "{name}"
    _fields: dict[str, Field]
    _object: ObjectManager

    _valid: bool | None = None
    _deleted: bool = False

    # Whether the form allows deletion of objects.
    # If set to True, the form will delete objects of form when the "_deleted"
    # field is present.
    _allow_delete: bool = False

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
                The messages are inherited to the forms of `FormSet` and `FormField` fields, however,
                if those forms have their own `messages` defined, those will take precendence over the
                parent messages.

        """
        self._fields = {}

        # Instead of regular dir(), that sorts by name
        for name in self.__dir__():
            if name.startswith("_") or name in ("is_valid", "is_invalid"):
                continue
            field = getattr(self, name)
            if not isinstance(field, Field):
                continue

            # Clone the field to avoid modifying the original class attribute
            field = copy(field)
            field.parent = self
            field.field_name = name
            self._fields[name] = field
            setattr(self, name, field)

        self._set_meta()
        self._object = self._ObjectManager(orm_cls=self.Meta.orm_cls)
        self._set_messages(messages or {})
        self._set_name_format(name_format)

        if reqdata is not None or object is not None:
            self._set(reqdata, object)

    def __repr__(self) -> str:
        attrs = []
        for name, field in self._fields.items():
            attrs.append(f"{name}={field.value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def __iter__(self):
        return iter(self._fields.values())

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

    @property
    def _delete(self) -> TextField:
        """
        Returns a fake field to render a hidden input to indicate
        that the object linked to this form should be deleted.
        """
        field = TextField(required=False)
        field.parent = self
        field.field_name = DELETED
        field.name_format = self._name_format
        return field

    @property
    def _destroy(self) -> TextField:
        """An alias to `Form._delete`."""
        return self._delete

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
                self._valid = False
                return False

        valid = self.on_after_validation()

        self._valid = valid
        return valid

    def save(self) -> t.Any:
        if not self._deleted and not self.is_valid:
            raise ValueError("Form is not valid", self.get_errors())

        if self._deleted:
            if not self._object.exists():
                return None
            if self._allow_delete:
                self._object.delete()
                return None
            else:
                logger.error("Deletion is not allowed for this form %s", self)

        data = {}
        for name, field in self._fields.items():
            data[name] = field.save()

        return self._object.save(data)

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
        self.Meta = copy(getattr(self, "Meta", DefaultMeta))

        orm_cls = getattr(self.Meta, "orm_cls", None)
        if (orm_cls is not None) and not isinstance(orm_cls, type):
            raise ValueError("Meta.orm_cls must be a class, not an instance.")
        self.Meta.orm_cls = orm_cls

        messages = getattr(self.Meta, "messages", {})
        if not isinstance(messages, dict):
            raise ValueError("Meta.messages must be a dictionary.")
        self.Meta.messages = messages

        pk = getattr(self.Meta, "pk", "id")
        if not isinstance(pk, str):
            raise ValueError("Meta.pk must be a string.")
        self.Meta.pk = pk

    def _set_messages(self, messages: dict[str, str]):
        self._messages = {**self.Meta.messages, **messages}
        for field in self._fields.values():
            field.set_messages(self._messages)

    def _set_name_format(self, name_format: str) -> None:
        self._name_format = name_format
        for field in self._fields.values():
            field.set_name_format(name_format)

    def _set(self, reqdata: t.Any = None, object: t.Any = None) -> None:
        self._valid = None

        reqdata = parse(reqdata or {})
        self._object = self._ObjectManager(
            orm_cls=self.Meta.orm_cls,
            object=object,
        )
        self._deleted = bool(reqdata.get(DELETED, None))

        if not self._deleted:
            for name, field in self._fields.items():
                field.set(reqdata.get(name), self._object.get(name))
