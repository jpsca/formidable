"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t
from collections.abc import Iterable

from .. import errors as err
from ..common import PK_NAME, get_pk
from .base import Field


if t.TYPE_CHECKING:
    from ..form import Form


class NestedForms(Field):
    """
    A field that represents a set of forms, allowing for dynamic addition and removal of forms.

    Args:
        FormClass:
            The class of the form to be used as a sub-form.
        min_items:
            Minimum number of form in the set. Defaults to None (no minimum).
        max_items:
            Maximum number of form in the set. Defaults to None (no maximum).
        default:
            Default value for the field. Defaults to `None`.
        allow_delete:
            Whether the form allows deletion of objects.
            If set to `True`, the form will delete objects of form when the "_destroy"
            field is present. Defaults to `True`.

    """

    def __init__(
        self,
        FormClass: "type[Form]",
        *,
        min_items: int | None = None,
        max_items: int | None = None,
        default: t.Any = None,
        allow_delete: bool = True,
    ):
        self.FormClass = FormClass
        self.empty_form = FormClass()

        self.forms = []
        self.pk = getattr(self.empty_form.Meta, "pk", "id")

        if min_items is not None and (not isinstance(min_items, int) or min_items < 0):
            raise ValueError("`min_items` must be a positive integer")
        self.min_items = min_items

        if max_items is not None and (not isinstance(max_items, int) or max_items < 0):
            raise ValueError("`max_items` must be a positive integer")
        self.max_items = max_items

        self.allow_delete = bool(allow_delete)

        super().__init__(
            required=bool(min_items),
            default=default,
            messages={**self.empty_form._messages},
        )
        self.set_name_format(self.name_format)

    def set_name_format(self, name_format: str):
        self.name_format = f"{name_format}[NEW_RECORD]"
        self.sub_name_format = f"{self.name}[{{name}}]"
        self.empty_form._set_name_format(self.sub_name_format)

    def set_messages(self, messages: dict[str, str]):
        super().set_messages(messages)
        self.empty_form._set_messages(self.messages)

    def set(
        self,
        reqvalue: dict[str, t.Any] | None = None,
        objvalue: Iterable[t.Any] | None = None,
    ):
        self.error = None
        self.error_args = None

        reqvalue = reqvalue or {}
        assert isinstance(reqvalue, dict), "reqvalue must be a dictionary"
        objvalue = objvalue or []
        assert isinstance(objvalue, Iterable), "objvalue must be an iterable"
        if not (reqvalue or objvalue):
            reqvalue = self.default_value or {}

        self.forms = []
        pks_used = set()

        reqvalue, objvalue = self._custom_filter(reqvalue, objvalue)
        index = 0

        if reqvalue:
            objects = {get_pk(obj, self.pk): obj for obj in objvalue}
            for data in reqvalue.values():
                pk = data.get(PK_NAME, None)
                # get_pk return str for non-None values, so this must be str as well
                pk = str(pk) if pk is not None else None

                self._add_form(
                    data=data,
                    object=objects.get(pk) if pk else None,
                    key=index,
                )
                if pk:
                    pks_used.add(pk)
                index += 1

        if objvalue:
            for obj in objvalue:
                pk = get_pk(obj, self.pk)
                if pk and pk in pks_used:
                    continue
                name_format = self.sub_name_format.replace("NEW_RECORD", str(index))
                form = self.FormClass(
                    object=obj,
                    name_format=name_format,
                    messages=self.messages,
                )
                form._allow_delete = self.allow_delete
                self.forms.append(form)
                if pk:
                    pks_used.add(pk)
                index += 1

    def build(self, num: int = 1) -> None:
        """
        Build a form and add it to the forms set.
        """
        for _ in range(num):
            self._add_form()

    def _add_form(
        self,
        data: t.Any = None,
        object: t.Any = None,
        key: int | None = None,
    ) -> "Form":
        key = key if key is not None else len(self.forms)
        name_format = self.sub_name_format.replace("NEW_RECORD", str(key))
        form = self.FormClass(
            data,
            object=object,
            name_format=name_format,
            messages=self.messages,
        )
        form._allow_delete = self.allow_delete
        self.forms.append(form)
        return form

    def save(self) -> list[t.Any]:
        """
        Save the forms in the forms set and return a list of the results.
        """
        results = []
        for form in self.forms:
            result = form.save()
            if result is None:
                continue
            results.append(result)
        return results

    def validate_value(self) -> bool:
        """
        Validate the field value against the defined constraints.
        """
        sub_errors = {}
        for index, form in enumerate(self.forms):
            if form.is_invalid:
                sub_errors[index] = form.get_errors()

        if sub_errors:
            self.error = err.INVALID
            self.error_args = sub_errors
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

    def _custom_filter(
        self,
        reqvalue: dict[str, t.Any] | None,
        objvalue: Iterable[t.Any],
    ) -> tuple[dict[str, t.Any] | None, Iterable[t.Any]]:
        return reqvalue, objvalue

