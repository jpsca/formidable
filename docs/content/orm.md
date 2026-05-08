---
title: ORM integration
---

In addition to returning dictionaries, Formidable can directly work with ORM models to create and update records in your database.

## Connecting Forms to Models

To enable this, you must add a `Meta` class to your form, with a `orm_cls` attribute pointing to the ORM model. For example:

```python {hl_lines="5-6"}
import formidable as f
from .models import Page

class PageForm(f.Form):
    class Meta:
        orm_cls = Page

    title = f.TextField()
    content = f.TextField()

```

### What `form.save()` does

For ORM-bound forms, `form.save()` returns a **fully persisted** object — no follow-up `obj.save()` or `session.commit()` is needed in the consumer:

- **No bound `object`** (a "create" form): calls `orm_cls.create(**data)` if available (the Peewee idiom — instantiates and INSERTs in one call); otherwise falls back to `orm_cls(**data); obj.save()` so detached SQLAlchemy / SQLModel instances are persisted too.
- **With a bound `object`** (an "update" form): setattrs the form data onto the object and then calls `object.save()` if the method exists. Plain dict objects get a `{**object, **data}` merge and are returned as-is.

### Transactional by default

When the form's `Meta.orm_cls` exposes Peewee's `_meta.database.atomic()` shape, the field-save loop and the object save run inside a single transaction. If a side-effecting field (e.g. an upload-then-INSERT field) succeeds but the parent's INSERT/UPDATE then fails, the prior INSERT is rolled back automatically — no orphans land in the database.

ORMs that don't expose that shape (SQLAlchemy session-flow, plain dicts) flow through unchanged; transaction management stays the consumer's responsibility for those.

To plug in a different transaction primitive (e.g. SQLAlchemy's `session.begin()`), override `Form._persistence_context()`:

```python {title="forms/base.py"}
import formidable as f
from contextlib import nullcontext
from .db import db_session

class BaseForm(f.Form):
    def _persistence_context(self):
        if self.Meta.orm_cls is None:
            return nullcontext()
        return db_session.begin()
```

### Peewee, Pony, and Tortoise ORM

These ORMs are zero-config: their models expose `create(**kwargs)` and `save()` methods, which is exactly the API `Form.save()` calls into. For Peewee specifically, the transactional-default kicks in automatically because Peewee models expose `_meta.database.atomic()`.

### SQLAlchemy and SQLModel

SQLAlchemy uses a session pattern rather than per-instance persistence, so the default `Form.save()` flow doesn't quite cover the "session.add + session.commit" handshake out of the box. Two ways to bridge:

#### Option A: Add methods to a model base class

Formidable's `ObjectManager` looks for `orm_cls.create(**data)` on construction and `object.delete()` when removing nested entries. Add them to a shared base:

```python {title="models/base.py"}
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        db_session.add(instance)
        return instance

    # Only needed for NestedForms fields
    def delete(self):
        db_session.delete(self)

```

Then use `Base` as the base for all your models:

```python {title="models/page.py"}
class Page(Base):
    __tablename__ = "pages"
    title: Mapped[str]
    content: Mapped[str]

```

You'll typically commit the session at request-end (e.g. via a middleware) rather than per-form.

#### Option B: Provide a custom ObjectManager

Alternatively, subclass `ObjectManager` to handle the session directly:

```python {title="forms/base.py"}
import formidable as f
from formidable.wrappers import ObjectManager

class SAObjectManager(ObjectManager):
    def create(self, data):
        instance = self.orm_cls(**data)
        db_session.add(instance)
        return instance

    # Only needed for NestedForms fields
    def delete(self):
        db_session.delete(self.object)

class BaseForm(f.Form):
    _ObjectManager = SAObjectManager

```

Then make all your forms inherit from it:

```python {title="forms/page.py", hl_lines="5"}
import formidable as f
from .models import Page
from .base import BaseForm

class PageForm(BaseForm):
    class Meta:
        orm_cls = Page

    title = f.TextField()
    content = f.TextField()

```

## Using Sub-forms (`FormField`)

::: div columns

```python {title="Scenario 1"}
class MetadataForm(f.Form):
    class Meta:
        orm_cls = PageMetadata

    description = f.TextField()
    keywords = f.ListField()

class PageForm(f.Form):
    class Meta:
        orm_cls = Page

    title = f.TextField()
    content = f.TextField()
    metadata = f.FormField(
        MetadataForm
    )

```

```python {title="Scenario 2"}
class MetadataForm(f.Form):
    description = f.TextField()
    keywords = f.ListField()

class PageForm(f.Form):
    class Meta:
        orm_cls = Page

    title = f.TextField()
    content = f.TextField()
    metadata = f.FormField(
        MetadataForm
    )

```

:::

* If the subform is connected to a model (scenario 1), an object will be created and returned.
* If the subform is *not* connected (scenario 2), `metadata` will be a dictionary.


## Using nested forms (`NestedForms`)

::: div columns

```python {title="Scenario 1"}
class IngredientForm(f.Form):
    class Meta:
        orm_cls = Ingredient

    name = f.TextField()
    quantity = f.FloatField()

class RecipeForm(f.Form):
    class Meta:
        orm_cls = Recipe

    title = f.TextField()
    instructions = f.TextField()
    ingredients = f.NestedForms(
        IngredientForm
    )
```

```python {title="Scenario 2"}
class IngredientForm(f.Form):
    name = f.TextField()
    quantity = f.FloatField()

class RecipeForm(f.Form):
    class Meta:
        orm_cls = Recipe

    title = f.TextField()
    instructions = f.TextField()
    ingredients = f.NestedForms(
        IngredientForm
    )
```
:::

* If the nested form is connected to a model (scenario 1), a *list of objects* will be returned.
* If the nested form is *not* connected (scenario 2), `ingredients` will be a *list of dictionaries*.

### Custom primary keys

`NestedForms` fields use the primary keys of objects to track them.

If your model uses a primary key field with a name other than `"id"`, you must specify the actual field name using the `pk` attribute in the form's `Meta` class:

```python {hl_lines="4"}
class IngredientForm(f.Form):
    class Meta:
        orm_cls = Ingredient
        pk = "code"


    name = f.TextField()
    quantity = f.FloatField()
```

### Deleting objects

Only nested forms can delete objects. A nested form will be marked for deletion when its request data includes a hidden field named `_destroy`. For more details about this feature, see the [Nested Forms](/docs/nested/) section.

Deletion is **disabled by default**. To enable it, pass `allow_delete=True` when instantiating a `NestedForms` field:

```python {hl_lines="14"}
class IngredientForm(f.Form):
    class Meta:
        orm_cls = Ingredient

    name = f.TextField()
    quantity = f.FloatField()

class RecipeForm(f.Form):
    class Meta:
        orm_cls = Recipe

    title = f.TextField()
    instructions = f.TextField()
    ingredients = f.NestedForms(IngredientForm, allow_delete=True)
```
