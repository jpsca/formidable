"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import pytest

import formidable as f


def test_reserved_words():
    for name in f.RESERVED_NAMES:
        with pytest.raises(ValueError):
            class TestForm(f.Form):
                locals()[name] = f.TextField()

            TestForm()


@pytest.mark.parametrize("name", ["is_valid", "is_invalid"])
def test_reserved_property_names(name):
    with pytest.raises(ValueError, match=f"Form cannot have a field named '{name}'"):
        attrs = {name: f.TextField()}
        FormCls = type("TestForm", (f.Form,), attrs)
        FormCls()


def test_field_inherited_from_grandparent():
    """MRO walk skips base classes that don't define the field."""
    class GrandParent(f.Form):
        name = f.TextField()

    class Parent(GrandParent):
        pass

    class Child(Parent):
        extra = f.TextField()

    form = Child({"name": "Alice", "extra": "val"})
    assert form.name.value == "Alice"
    assert form.extra.value == "val"


def test_non_field_attribute_set_to_none():
    """Attribute set to None in class dict is skipped (not a Field)."""
    class MyForm(f.Form):
        phantom = None
        name = f.TextField()

    assert "name" in MyForm._field_names
    assert "phantom" not in MyForm._field_names


def test_contains():
    class TestForm(f.Form):
        a = f.TextField()
        b = f.TextField()
        c = f.TextField()

    form = TestForm()

    assert "a" in form
    assert list(form) == [form.a, form.b, form.c]


def test_no_errors():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({"name": "John"})
    form.validate()

    assert form.is_valid
    assert form.name.error is None
    assert form.get_errors() == {}


def test_errors():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.is_invalid
    assert form.name.error == "required"
    assert form.get_errors() == {"name": "required"}


def test_all_field_errors_reported():
    class TestForm(f.Form):
        name = f.TextField()
        email = f.TextField()
        age = f.IntegerField()

    form = TestForm({})
    form.validate()

    assert form.is_invalid
    errors = form.get_errors()
    assert "name" in errors
    assert "email" in errors
    assert "age" in errors
    assert len(errors) == 3


def test_save_invalid_form():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm({})

    with pytest.raises(ValueError):
        form.save()


def test_invalid_orm_cls():
    with pytest.raises(ValueError):
        class TestForm(f.Form):
            class Meta:
                orm_cls = "lol"

            name = f.TextField()


def test_invalid_custom_messages():
    with pytest.raises(ValueError):
        class TestForm(f.Form):
            class Meta:
                messages = "lol"

            name = f.TextField()


def test_invalid_custom_pk():
    with pytest.raises(ValueError):
        class TestForm(f.Form):
            class Meta:
                pk = None

            name = f.TextField()


def test_custom_messages():
    MSG = "Custom required message in Meta"

    class TestForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.name.error == "required"
    assert form.name.error_message == MSG


def test_meta_is_inherited():
    class Model:
        pass

    class BaseForm(f.Form):
        class Meta:
            orm_cls = Model
            pk = "code"
            messages = {"required": "Give me the value!"}

    class TestForm(BaseForm):
        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.Meta.orm_cls is Model
    assert form.Meta.pk == "code"
    assert form.name.error_message == "Give me the value!"


def test_own_meta_extends_the_inherited_one():
    class Model:
        pass

    class BaseForm(f.Form):
        class Meta:
            pk = "code"
            messages = {"required": "Base required", "invalid": "Base invalid"}

    class TestForm(BaseForm):
        class Meta:
            orm_cls = Model
            messages = {"required": "Own required", "taken": "Already taken"}

        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.Meta.orm_cls is Model
    assert form.Meta.pk == "code"
    assert form.Meta.messages == {
        "required": "Own required",
        "invalid": "Base invalid",
        "taken": "Already taken",
    }
    assert form.name.error_message == "Own required"
    # The parent form is not changed
    assert BaseForm().Meta.orm_cls is None
    assert BaseForm().Meta.messages == {
        "required": "Base required",
        "invalid": "Base invalid",
    }


def test_own_meta_can_replace_the_inherited_options():
    class Model:
        pass

    class BaseForm(f.Form):
        class Meta:
            orm_cls = Model
            pk = "code"

    class TestForm(BaseForm):
        class Meta:
            orm_cls = None
            pk = "id"

    assert TestForm().Meta.orm_cls is None
    assert TestForm().Meta.pk == "id"


def test_meta_is_inherited_from_grandparent():
    class GrandParentForm(f.Form):
        class Meta:
            messages = {"required": "From the grandparent"}

    class ParentForm(GrandParentForm):
        pass

    class TestForm(ParentForm):
        class Meta:
            pk = "code"

        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.Meta.pk == "code"
    assert form.name.error_message == "From the grandparent"


def test_meta_class_can_inherit_from_another_meta():
    class Model:
        pass

    class BaseForm(f.Form):
        class Meta:
            messages = {"required": "Give me the value!"}

    class TestForm(BaseForm):
        class Meta(BaseForm.Meta):
            orm_cls = Model

        name = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.Meta.orm_cls is Model
    assert form.name.error_message == "Give me the value!"


def test_invalid_custom_messages_in_a_child_form():
    class BaseForm(f.Form):
        class Meta:
            messages = {"required": "Give me the value!"}

    with pytest.raises(ValueError):
        class TestForm(BaseForm):
            class Meta:
                messages = "lol"


def test_field_messages():
    MSG = "Custom required message in field"

    class TestForm(f.Form):
        name1 = f.TextField(messages={"required": MSG})
        name2 = f.TextField()

    form = TestForm({})
    form.validate()
    assert form.name1.error == "required"
    assert form.name2.error == "required"
    assert form.name1.error_message == MSG
    assert form.name2.error_message != MSG


def test_field_messages_overrides_form_messages():
    MSG_FORM = "Form required message"
    MSG_FIELD = "Field required message"

    class TestForm(f.Form):
        class Meta:
            messages = {"required": MSG_FORM}

        name1 = f.TextField(messages={"required": MSG_FIELD})
        name2 = f.TextField()

    form = TestForm({})
    form.validate()

    assert form.name1.error == "required"
    assert form.name1.error_message == MSG_FIELD
    assert form.name2.error == "required"
    assert form.name2.error_message == MSG_FORM


def test_messages_inheritance_with_form_field():
    MSG = "parent"

    class ChildForm(f.Form):
        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        ff = f.FormField(ChildForm)

    form = ParentForm({"ff[name]": ""})
    form.validate()

    assert form.ff.form.name.error == "required"  # type: ignore
    assert form.ff.form.name.error_message == MSG  # type: ignore


def test_messages_override_with_form_field():
    MSG_PARENT = "parent"
    MSG_CHILD = "child"

    class ChildForm(f.Form):
        class Meta:
            messages = {"required": MSG_CHILD}

        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG_PARENT}

        ff = f.FormField(ChildForm)

    form = ParentForm({"ff[name]": ""})
    form.validate()

    assert form.ff.form.name.error == "required"  # type: ignore
    assert form.ff.form.name.error_message == MSG_CHILD  # type: ignore


def test_messages_inheritance_with_nested_field():
    MSG = "parent"

    class ChildForm(f.Form):
        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG}

        myset = f.NestedForms(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG


def test_messages_override_with_nested_field():
    MSG_PARENT = "parent"
    MSG_CHILD = "child"

    class ChildForm(f.Form):
        class Meta:
            messages = {"required": MSG_CHILD}

        name = f.TextField()

    class ParentForm(f.Form):
        class Meta:
            messages = {"required": MSG_PARENT}

        myset = f.NestedForms(ChildForm)

    form = ParentForm({"myset[0][name]": ""})
    form.validate()

    assert form.myset.forms[0].name.error == "required"
    assert form.myset.forms[0].name.error_message == MSG_CHILD


def test_custom_filter():
    class TestForm(f.Form):
        name = f.TextField(required=False)

        def filter_name(self, value):
            return value.upper()

    form = TestForm({"name": "Zoe"})
    assert form.is_valid
    assert form.name.value == "ZOE"


def test_custom_filter_with_error():
    class TestForm(f.Form):
        name = f.TextField(required=False)

        def filter_name(self, value):
            if value and value.startswith("Z"):
                raise ValueError("no-z-names")
            return value

    form = TestForm({"name": "Zoe"})
    assert form.is_invalid
    assert form.name.error == "no-z-names"

    form = TestForm({})
    assert form.is_valid


def test_custom_validator():
    class TestForm(f.Form):
        name = f.TextField()

        def validate_name(self, value):
            return value.upper()

    form = TestForm({"name": "Zoe"})
    assert form.is_valid
    assert form.name.value == "ZOE"


def test_custom_validator_with_error():
    class TestForm(f.Form):
        name = f.TextField()

        def validate_name(self, value):
            if value.startswith("Z"):
                raise ValueError("no-z-names")
            return value

    form = TestForm({"name": "Zoe"})
    assert form.is_invalid
    assert form.name.error == "no-z-names"


def test_boolean_custom_filter_with_error():
    class TestForm(f.Form):
        bool = f.BooleanField()

        def filter_bool(self, value):
            if value == "maybe":
                raise ValueError("not-an-answer")
            return value

    form = TestForm({"bool": "maybe"})
    assert form.is_invalid


def test_file_custom_filter_with_error():
    class TestForm(f.Form):
        photo = f.FileField()

        def filter_photo(self, value):
            raise ValueError("you-shall-not-pass")

    form = TestForm({"photo": "test.jpg"})
    assert form.is_invalid


def test_form_validation():
    class TestForm(f.Form):
        password1 = f.TextField()
        password2 = f.TextField()

        def after_validate(self):
            if self.password1.value != self.password2.value:
                self.password2.error = "invalid"
                return False
            return True

    form = TestForm({"password1": "abc", "password2": "abc"})
    assert form.is_valid

    form = TestForm({"password1": "abc", "password2": "def"})
    assert form.is_invalid


def test_hidden_tags():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm()
    assert str(form.hidden_tags()) == ""


def test_hidden_tags_with_object():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm(object={"id": 42})
    expected = (
        '<input type="hidden" name="_id" value="42" />'
    )
    assert str(form.hidden_tags()) == expected


def test_hidden_tags_with_fake_object():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm(object={"name": "meh"})
    assert str(form.hidden_tags()) == ""


def test_hidden_tags_full():
    class TestForm(f.Form):
        name = f.TextField()

    form = TestForm(object={"id": 42})
    form._allow_delete = True
    expected = (
        '<input type="hidden" name="_destroy" />\n'
        '<input type="hidden" name="_id" value="42" />'
    )
    assert str(form.hidden_tags()) == expected


# ── Form._persistence_context ──────────────────────────────────────────────


class _FakeAtomic:
    """Mimics the peewee `db.atomic()` interface enough to verify wiring:
    enter/exit are recorded, and exceptions propagate (mirroring peewee's
    actual behavior of rolling back on __exit__ when exc is non-None).
    """

    def __init__(self):
        self.enter_count = 0
        self.exit_count = 0
        self.last_exc_type = None

    def __call__(self):
        return self

    def __enter__(self):
        self.enter_count += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exit_count += 1
        self.last_exc_type = exc_type
        return False  # propagate exceptions


class _FakeMeta:
    def __init__(self, atomic):
        self.database = type("DB", (), {"atomic": atomic})()


class _FakeOrmCls:
    """ORM-class shim: exposes peewee's `_meta.database.atomic()` shape but
    keeps `create()` so ObjectManager.save can take its create branch.
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def _bind(cls, atomic):
        cls._meta = _FakeMeta(atomic)
        return cls

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


def test_persistence_context_wraps_save_when_orm_exposes_atomic():
    """For ORMs that expose peewee's `_meta.database.atomic()` shape, the
    field-save loop and the object save run inside that context manager.
    """
    atomic = _FakeAtomic()
    OrmCls = type("Orm", (_FakeOrmCls,), {})._bind(atomic)

    class ProductForm(f.Form):
        class Meta:
            orm_cls = OrmCls

        name = f.TextField()

    form = ProductForm({"name": ["test"]})
    form.save()

    assert atomic.enter_count == 1
    assert atomic.exit_count == 1
    assert atomic.last_exc_type is None  # clean exit


def test_persistence_context_rolls_back_on_failure():
    """An exception raised during the field-save loop or object save must
    propagate through the context manager so peewee's atomic() rolls back.
    """
    atomic = _FakeAtomic()
    OrmCls = type("Orm", (_FakeOrmCls,), {})._bind(atomic)

    class ExplodingField(f.TextField):
        def save(self):
            raise RuntimeError("boom")

    class ProductForm(f.Form):
        class Meta:
            orm_cls = OrmCls

        name = ExplodingField()

    form = ProductForm({"name": ["test"]})
    with pytest.raises(RuntimeError, match="boom"):
        form.save()

    assert atomic.enter_count == 1
    assert atomic.exit_count == 1
    assert atomic.last_exc_type is RuntimeError


def test_persistence_context_is_noop_for_non_peewee_orm():
    """ORMs that don't expose `_meta.database.atomic()` (SQLAlchemy, plain
    classes) must flow through unchanged — no transaction wrapping.
    """
    class PlainOrm:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        @classmethod
        def create(cls, **kwargs):
            return cls(**kwargs)

    class ProductForm(f.Form):
        class Meta:
            orm_cls = PlainOrm

        name = f.TextField()

    # Should not raise even though PlainOrm has no _meta/database/atomic.
    form = ProductForm({"name": ["test"]})
    obj = form.save()
    assert isinstance(obj, PlainOrm)
    assert obj.name == "test"


def test_persistence_context_is_noop_for_dict_form():
    """Forms with no orm_cls (returning a data dict) must not attempt any
    transaction wrapping — `nullcontext` keeps the path side-effect free.
    """

    class DataForm(f.Form):
        name = f.TextField()

    data = DataForm({"name": ["x"]}).save()
    assert data == {"name": "x"}
