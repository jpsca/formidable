---
title: FormSet
---

::: formidable.FormSet members=no

This is a powerful field. The idea is to allow users to dynamically add or remove one or more instances of a subform.

```python
class IngredientForm(f.Form):
    name = f.TextField()
    quantity = f.FloatField()


class RecipeForm(f.Form):
    title = f.TextField()
    instructions = f.TextField()
    ingredients = f.FormSet(IngredientForm)

```

In a database this is equivalent to a one-to-many relationship (in this example one `Recipe` has many `Ingredients`).

There is a lot to unpack, so this field has its own section: [Nested Forms](/docs/nested/).
