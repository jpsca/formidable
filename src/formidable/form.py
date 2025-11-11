"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import logging
import typing as t
from copy import copy

from markupsafe import Markup

from .common import DELETED_NAME, PK_NAME, get_pk
from .fields.base import Field
from .fields.text import TextField
from .parser import parse
from .wrappers import ObjectManager


RESERVED_NAMES = (
    "get_errors",
    "save",
    "validate",
    "after_validate",
)

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
    """
    Base class for creating forms.

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
            The messages are inherited to the forms of `NestedForms` and `FormField` fields, however,
            if those forms have their own `messages` defined, those will take precendence over the
            parent messages.

    """

    # The class to use for wrapping objects in the form.
    _ObjectManager: type[ObjectManager] = ObjectManager

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
        self._fields = {}

        # Instead of regular dir(), that sorts by name
        for name in self.__dir__():
            if name.startswith("_") or name in ("is_valid", "is_invalid", "hidden_tags"):
                continue

            field = getattr(self, name)
            if not isinstance(field, Field):
                continue

            if name in RESERVED_NAMES:
                raise ValueError(f"Form cannot have a field named '{name}'")

            # Clone the field to avoid modifying the original class attribute
            field = copy(field)
            field.parent = self
            field.field_name = name

            custom_filter = getattr(self, f"filter_{name}", None)
            if callable(custom_filter):
                field._custom_filter = custom_filter

            custom_validator = getattr(self, f"validate_{name}", None)
            if callable(custom_validator):
                field._custom_validator = custom_validator

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

        This is a property with side effects: it triggers validation of all fields
        and the form itself.

        It wasn't designed as a method to prevent the common mistake of forgetting
        to call it, which would lead to incorrect assumptions about the form's validity.

        The result is cached, so to re-validate the form, you need to call `form.validate()`.
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
    def hidden_tags(self) -> str:
        """
        Returns hidden inputs for dealing with objects in nested forms
        """
        delete_tag = self._delete_tag
        pk_tag = self._pk_tag
        if pk_tag:
            return Markup(f"{delete_tag}\n{pk_tag}")
        return Markup(delete_tag)

    @property
    def _delete_tag(self) -> str:
        """
        Returns a hidden input for marking the form as deleted.
        """
        delete_field = TextField(required=False)
        delete_field.parent = self
        delete_field.field_name = DELETED_NAME
        delete_field.name_format = self._name_format
        return delete_field.hidden_input()

    @property
    def _pk_tag(self) -> str:
        """
        Returns a hidden input for the primary key of the object.
        """
        if self._object.exists():
            pk_name = getattr(self.Meta, "pk", "id")
            pk = get_pk(self._object.object, pk_name)
            if pk:
                pk_field = TextField(required=False)
                pk_field.parent = self
                pk_field.field_name = PK_NAME
                pk_field.name_format = self._name_format
                pk_field.value = pk
                return pk_field.hidden_input()
        return ""

    def get_errors(self) -> dict[str, str]:
        """
        Returns a dictionary of field names and their error messages.
        """
        errors = {}
        for name, field in self._fields.items():
            if field.error is not None:
                errors[name] = field.error
        return errors

    def save(self, **extra) -> t.Any:
        """
        Saves the form data.

        If the form is valid, this method will collect all the field values and:

        a) If the form is not connected to an ORM model and it wasn't instantiate with
           an object, it will return the data as a dictionary.
        b) If it *was* instantiate with an object, it will update and return the object
           (even if the "object" in question is a dictionary).
        c) If it *wasn't* instantiate with an object, but it is connected to an ORM model,
           it will create a new object and return it.

        Args:
            **extra:
                Extra data to pass to add to the data before saving. This is useful
                to set fields that are not part of the form (e.g.: foreign keys).

        """

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

        data.update(extra)
        return self._object.save(data)

    def validate(self) -> bool:
        """
        Triggers validation of each of the fields and the form itself.

        Returns:
            `True` or `False`, whether the form is valid after validation.

        """
        self._valid = True

        for field in self._fields.values():
            field.validate()
            if field.error is not None:
                self._valid = False
                return False

        self._valid = self.after_validate()
        return self._valid

    def after_validate(self) -> bool:
        """
        Called after the individual field validations.

        You can use to validate the relation between fields (e.g.: `password1 == password2`)
        or to modify the field values before saving.

        To indicate validation errors, set the `error` attribute of the individual fields.

        Returns:
            `True` or `False`, whether the form is valid after the custom validation.

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
        self._deleted = bool(reqdata.get(DELETED_NAME, None))

        if not self._deleted:
            for name, field in self._fields.items():
                field.set(reqdata.get(name), self._object.get(name))
