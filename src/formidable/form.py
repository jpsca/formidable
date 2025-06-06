"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t

from .fields.base import Field
from .parser import parse
from .wrappers import ObjectWrapper


MESSAGES = {
    "invalid": "Invalid value for {name}",
    "required": "Field {name} is required",
}

class Form:
    """

    """
    class Meta:
        orm_cls: t.Any = None
        messages: dict[str, str]

    _fields: tuple[str, ...]
    _object: ObjectWrapper | None = None
    _valid: bool | None = None

    def __init__(
            self,
            reqdata: t.Any = None,
            object: t.Any = None,
            *,
            name_format: str = "{name}",
        ):
        self._set_messages()

        fields = []
        for name in self.__dir__():  # Instead of regular dir() that sorts by name
            if name.startswith("_"):
                continue
            field = getattr(self, name)
            if not isinstance(field, Field):
                continue
            field.parent = self
            field.field_name = name
            field.set_messages(self.Meta.messages)
            fields.append(name)

        self._fields = tuple(fields)
        self._set_name_format(name_format)
        self._set(parse(reqdata), object)

    def __repr__(self):
        attrs = []
        for name in self._fields:
            field = getattr(self, name)
            attrs.append(f"{name}={field.value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

    def _set_messages(self, messages: dict[str, str] | None = None):
        self.Meta.messages = messages or getattr(self.Meta, "messages", MESSAGES)

    def _set_name_format(self, name_format: str):
        for name in self._fields:
            field = getattr(self, name)
            field.set_name_format(name_format)

    def _set(self, reqdata: t.Any = None, object: t.Any = None):
        self._valid = False
        reqdata = reqdata or {}
        self._object = wr_object = ObjectWrapper(object)
        for name in self._fields:
            field = getattr(self, name)
            field.set(reqdata.get(name), wr_object.get(name))

    def get_errors(self) -> dict[str, str]:
        """
        Returns a dictionary of field names and their error messages.
        """
        errors = {}
        for name in self._fields:
            field = getattr(self, name)
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
        for name in self._fields:
            field = getattr(self, name)
            field.validate()
            if field.error is not None:
                valid = False

        self._valid = valid
        return valid

    def save(self) -> t.Any:
        if not self.is_valid:
            raise ValueError("Form is not valid")

        data = {}
        for name in self._fields:
            field = getattr(self, name)
            data[name] = field.save()

        if self._object:
            return self._object.update(data)

        if self.Meta.orm_cls:
            return self.Meta.orm_cls(**data)

        return data
