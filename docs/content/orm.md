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

### Peewee, Pony, and Tortoise ORM

For these ORMs, the integration is automatic.

After calling `form.save()`, you only need to commit the changes to the database:
- For Pony ORM, use `db_session.commit()`
- For Peewee and Tortoise ORM, use `myobject.save()`

### SQLAlchemy and SQLModel

Because these ORMs work with a session pattern, Formidable's default `ObjectManager` needs to be extended. There are two ways to do this:

#### Option A: Add methods to a model base class

Formidable's `ObjectManager` calls `orm_cls.create(**data)` when creating new objects and `object.delete()` when deleting them. You can add these methods to a shared model base class:

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

#### Option B: Provide a custom ObjectManager

Alternatively, you can subclass `ObjectManager` to handle the session directly:

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
