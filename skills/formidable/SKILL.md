---
name: formidable
description: Build, render, and validate web forms with the Formidable Python library. Use when the user works with `formidable as f`, subclasses `f.Form`, uses fields like `f.TextField`, `f.NestedForms`, `f.FormField`, or asks how to render/validate/save a form, integrate with an ORM, or handle nested/dynamic forms.
---

# Formidable

A small Python library for rendering and processing web forms. HTML-first (works well with HTMX/Turbo), ORM-agnostic (Peewee, Pony, Tortoise, SQLAlchemy, SQLModel), with first-class support for **subforms** (`FormField`) and **dynamic nested forms** (`NestedForms`).

Install: `uv add formidable` or `pip install formidable`. Always import as `import formidable as f`.

## Core mental model

A `Form` subclass declares fields as class attributes. You instantiate it with up to two sources of data:

```python
form = MyForm()                      # empty
form = MyForm(request_data)          # from a submitted form
form = MyForm({}, object)            # from an existing object (edit view)
form = MyForm(request_data, object)  # submitted edit — request wins over object
```

- `request_data` is the framework's form dict (e.g. `request.form` in Flask) — a multi-dict. For tests, `{"key": [value]}` works.
- `object` is a model instance or plain dict used as a fallback source.

The typical controller flow:

```python
form = MyForm(request.form)
if form.is_invalid:
    return render_template("form.html", form=form)  # errors populated
data = form.save()  # dict, or ORM object if Meta.orm_cls is set
```

## Validation is explicit

**Field errors (`field.error`, `field.error_args`) are only populated after `form.validate()` runs** (or `form.is_valid` / `form.is_invalid`, which call `validate()` internally and cache the result). Just instantiating a form with partial data does *not* expose errors — this is intentional, so the first render of an edit view or empty form doesn't show pre-filled "required" errors.

Internally, `field.set()` records a pending error in `field._error`; `validate()` promotes it to `field.error`. In `after_validate()` (which runs *after* validate), it's fine to assign `self.some_field.error = "..."` directly.

Re-validate by calling `form.validate()` explicitly — the `is_valid` result is cached.

## Fields

All live on `formidable` and accept at least `required=True`, `default=None`, `messages={}`. Common ones:

| Field | Key extras |
|---|---|
| `TextField` | `strip`, `min_length`, `max_length`, `pattern` (regex str), `one_of` |
| `EmailField` | `one_of` |
| `URLField` | `schemes`, `one_of` |
| `SlugField` | |
| `IntegerField` / `FloatField` / `NumberField` | `gt`, `gte`, `lt`, `lte`, `multiple_of`, `one_of` |
| `BooleanField` | `required` defaults to `False`; truthy unless value is in `("false", "0", "no")` |
| `DateField` / `DateTimeField` / `TimeField` | `after_*`, `before_*`, `past_*`, `future_*`, `one_of` |
| `ListField(type=..., strict=False)` | `min_items`, `max_items`, `one_of`. Default is `[]`. |
| `FileField` | Does **not** handle uploads — only renders the input and tracks the filename. |
| `FormField(OtherForm)` | Embeds a single subform (one-to-one / JSON-like grouping). |
| `NestedForms(OtherForm, min_items=, max_items=, allow_delete=False)` | Dynamic list of subforms (one-to-many). |

Reserved field names that will raise at class creation: `is_valid`, `is_invalid`, `hidden_tags`, `get_errors`, `save`, `validate`, `after_validate`. Field names can't start with `_`.

## Custom filters and validators

Add methods named `filter_<fieldname>` or `validate_<fieldname>` on the form class.

```python
class MyForm(f.Form):
    name = f.TextField()

    def filter_name(self, value):
        return value.lower() if value else value  # transform

    def validate_name(self, value):
        if "e" not in (value or ""):
            raise ValueError("invalid")  # error code
        return value
```

Filters run inside `set()`; validators run inside `validate()`. To raise with extra context for message formatting: `raise ValueError("must_contain", {"char": "&"})` — the dict lands in `field.error_args`.

## Form-level validation

Override `after_validate(self) -> bool` to check cross-field invariants (password confirmation, etc.). Set errors via direct assignment:

```python
def after_validate(self) -> bool:
    if self.password1.value != self.password2.value:
        self.password2.error = "passwords_mismatch"
        return False
    return True
```

## Rendering

Fields expose render helpers that produce `Markup` (safe HTML). Chain them in templates:

```html+jinja
<div class="field">
  {{ form.name.label("Name") }}
  {{ form.name.text_input() }}
  {{ form.name.error_tag() }}
</div>
```

All render helpers accept arbitrary kwargs as HTML attributes (`class_="..."` becomes `class="..."`, `data_foo` becomes `data-foo`, booleans render as valueless attributes).

Helper families:
- **Label/error:** `label(text=None, **attrs)`, `error_tag(**attrs)`
- **Text-ish inputs:** `text_input`, `textarea`, `password_input`, `email_input`, `url_input`, `search_input`, `tel_input`, `color_input`, `number_input`, `range_input`, `date_input`, `datetime_input`, `time_input`, `month_input`, `week_input`, `file_input`, `hidden_input`
- **Choice inputs:** `select(options)` (auto-adds `multiple` when field is `multiple=True`), `checkbox()`, `radio(radio_value)`

Low-level attributes for hand-rolled HTML: `field.id`, `field.name`, `field.value`, `field.error`, `field.error_args`, `field.error_message`.

When `field.error` is set, the input helpers automatically add `aria-invalid="true"` and `aria-errormessage="{id}-error"` — pair them with `error_tag()` for accessible forms.

## Messages and i18n

Field errors are short *codes* (e.g. `"required"`, `"min_length"`). The `error_message` property resolves them against a messages dict (placeholders use `error_args`):

- **Global defaults:** `formidable.errors.MESSAGES`.
- **Per-form override:** `class Meta: messages = {"required": "..."}`. Extends, doesn't replace.
- **Per-field override:** `f.TextField(messages={"required": "..."})`.
- **Per-instance (i18n):** `MyForm(reqdata, messages=MESSAGES[user.locale])`.
- **Template-side i18n:** skip `messages` and use `{{ _(field.error) }}` with your own translation function.

## ORM integration

Add a `Meta.orm_cls` pointing to the model class:

```python
class PageForm(f.Form):
    class Meta:
        orm_cls = Page
    title = f.TextField()
```

Behavior of `form.save()`:
- **No `orm_cls` and no `object`:** returns a `dict`.
- **With `object`:** updates and returns it (works for dicts too).
- **With `orm_cls` and no `object`:** creates and returns a new instance (via `orm_cls.create(**data)`).

Peewee / Pony / Tortoise work out of the box (you still commit via your ORM). **SQLAlchemy / SQLModel** need you to either add a `create` classmethod to a shared `Base` class, or subclass `ObjectManager` and set `_ObjectManager` on a base form.

`form.save(**extra)` merges extra kwargs before persisting — great for attaching `user_id=request.user.id` without exposing it as a form field.

Custom primary key: `class Meta: pk = "code"` (default `"id"`).

## Subforms — `FormField`

Embeds a single nested form. The saved output groups its fields under that key:

```python
class Profile(f.Form):
    name = f.TextField()
    settings = f.FormField(SettingsForm)

# form.save() -> {"name": "...", "settings": {"locale": "...", ...}}
```

If `SettingsForm` has its own `Meta.orm_cls`, the nested value is a model instance; otherwise a dict. Useful for JSON columns or one-to-one relationships.

## Nested forms — `NestedForms`

A dynamic list of subforms (one-to-many). Each entry gets its own form instance.

```python
class RecipeForm(f.Form):
    class Meta:
        orm_cls = Recipe
    title = f.TextField()
    ingredients = f.NestedForms(IngredientForm, allow_delete=True)
```

Render loop:

```html+jinja
{% for sub in form.ingredients.forms %}
  {{ sub.hidden_tags() }}   {# renders _id and _destroy inputs #}
  {{ sub.name.text_input() }}
  ...
{% endfor %}
```

- **`hidden_tags()`** is mandatory on each subform — it emits `_id` (for object tracking) and `_destroy` (soft-delete marker) inputs.
- **`form.ingredients.build(n)`** pre-populates `n` blank subforms — typical for a "new" view so users see at least one.
- **`form.ingredients.empty_form`** returns a blank template instance for cloning in JS.
- **`allow_delete=True`** enables deletion via a `_destroy` field (also requires a matching UI control).
- **`_id` values are validated** against the objects passed to the form — users can't inject IDs for records they don't own.

### Dynamic add/remove in the browser

Formidable ships `nestedform.js` at `src/formidable/nestedform.js`. Include it as a module, then:

1. Mark the wrapper with `data-nestedform`.
2. Add `class="nestedform"` to each subform wrapper.
3. Add a `<button data-nestedform-remove>` inside each subform.
4. Add a `<template data-nestedform-template>` containing `{{ render_macro(form.foo.empty_form, "...") }}`.
5. Add `<div data-nestedform-target></div>` where new entries should land.
6. Add `<button data-nestedform-add>` to trigger insertion.

The script literally clones the `<template>`, so the macro must render the same markup used for existing subforms.

## Idiomatic patterns

**New view:**
```python
form = RecipeForm()
form.ingredients.build(1)  # optional: show one empty subform
```

**Create:**
```python
form = RecipeForm(request.form)
if form.is_invalid:
    return render_template(...)
recipe = form.save(user_id=current_user.id)
db.session.commit()  # whatever your ORM needs
```

**Edit:**
```python
form = RecipeForm({}, object=recipe)
```

**Update:**
```python
form = RecipeForm(request.form, object=recipe)
if form.is_invalid:
    return render_template(...)
form.save()
```

**Translating errors in templates:**
```html+jinja
{% if field.error %}<div class="err">{{ _(field.error) }}</div>{% endif %}
```

## Gotchas

- **Don't check `field.error` before validation.** It will be `None` until `validate()` runs. Use `form.is_invalid` as the gate.
- **`hidden_tags()` is easy to forget** on `NestedForms` subforms; without it, edits will create new rows instead of updating existing ones.
- **`BooleanField` defaults to `required=False`** because browsers don't send unchecked checkboxes. Set `required=True` only when you want to enforce "must be checked" (e.g. ToS agreement).
- **`FileField` does not upload** — wire that up in your framework layer.
- **Deep form inheritance is discouraged.** Prefer composition (mixins, `FormField`).
- **SQLAlchemy/SQLModel require a `create` method** on the model or a custom `ObjectManager` — otherwise `form.save()` fails on insert.
- **Reserved names** on forms: redefining `validate`, `save`, `is_valid`, etc. as fields raises at class-creation time.
