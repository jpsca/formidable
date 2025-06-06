"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from .base import Field


if t.TYPE_CHECKING:
    from ..form import Form


class FormSet(Field):
    def __init__(
        self,
        form_cls: "type[Form]",
        *,
        min_items: int | None = None,
        max_items: int | None = None,
        default: dict | None = None,
    ):
        """
        A field that represents a set of forms, allowing for dynamic addition and removal of forms.

        Arguments:

        - form_cls: The class of the form to be used as a sub-form.
        - min_items: Minimum number of form in the set. Defaults to None (no minimum).
        - max_items: Maximum number of form in the set. Defaults to None (no maximum).
        - default: Default value for the field. Defaults to `None`.

        """
        self.form_cls = form_cls
        self.new_form = form_cls()
        self.forms = []
        self.pk = getattr(form_cls.Meta, "pk", "id")

        if min_items is not None and (not isinstance(min_items, int) or min_items < 0):
            raise ValueError("`min_items` must be a positive integer")
        self.min_items = min_items

        if max_items is not None and (not isinstance(max_items, int) or max_items < 0):
            raise ValueError("`max_items` must be a positive integer")
        self.max_items = max_items

        if default is not None and not isinstance(default, dict):
            raise ValueError("`default` must be a dictionary or `None`")
        super().__init__(required=bool(min_items), default=default)

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[NEW_INDEX]"
        self.sub_name_format = f"{self.name}[{{name}}]"
        self.new_form._set_name_format(self.sub_name_format)

    def set(
        self,
        reqvalue: dict[str, t.Any] | None = None,
        objvalue: Iterable[t.Any] | None = None,
    ):
        reqvalue = reqvalue or {}
        assert isinstance(reqvalue, dict), "reqvalue must be a dictionary"
        objvalue = objvalue or []
        assert isinstance(objvalue, Iterable), "objvalue must be an iterable"
        if not (reqvalue or objvalue):
            reqvalue = self.default_value or {}

        self.error = None
        if reqvalue:
            objects = {getattr(obj, self.pk): obj for obj in objvalue}
            for pk, data in reqvalue.items():
                name_format = self.sub_name_format.replace("NEW_INDEX", pk)
                form = self.form_cls(
                    data, object=objects.get(pk), name_format=name_format
                )
                self.forms.append(form)

        else:
            for obj in objvalue:
                pk = getattr(obj, self.pk)
                name_format = self.sub_name_format.replace("NEW_INDEX", str(pk))
                form = self.form_cls(object=obj, name_format=name_format)
                self.forms.append(form)

    def save(self) -> list[t.Any]:
        """
        Save the forms in the formset and return a list of the results.
        """
        results = []
        for form in self.forms:
            result = form.save()
            if result is not None:
                results.append(result)
        return results

    def validate(self):
        """
        Validate the field value against the defined constraints.
        """
        if self.error is not None:
            return False

        if self.min_items is not None and len(self.forms) < self.min_items:
            self.error = err.MIN_ITEMS
            self.error_args = {"min_items": self.min_items}
            return False

        if self.max_items is not None and len(self.forms) > self.max_items:
            self.error = err.MAX_ITEMS
            self.error_args = {"max_items": self.max_items}
            return False

        return True
