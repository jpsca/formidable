---
title: Forms
---

Forms provide the highest-level API in Formidable. They contain your field definitions, handle validation, process input, and orchestrate everything together.

::: api formidable.Form
:show_members: false
:::


## Defining Forms

To define a form, create a subclass of `formidable.Form` and define the fields declaratively as class attributes:

```python
import formidable as f

class MyForm(f.Form):
    first_name = f.TextField()
    last_name = f.TextField(required=False)

```

Field names can be any valid python identifier, with the following restrictions:

* Field names are case-sensitive.
* Field names may not begin with "_" (underscore)
* Fields cannot be named `is_valid`, `is_invalid`, `hidden_tags`, `get_errors`, `save`, `validate`, or `after_validate`, as these names are reserved for form properties and methods.


### Form Inheritance

Forms may subclass other forms as needed. The new form will contain all fields of the parent form, as well as any new fields defined on the subclass. A field name re-used on a subclass causes the new definition to obscure the original.

```python
import formidable as f

class BasePostForm(f.Form):
    title = f.TextField()
    content = f.TextField()


LAYOUTS = ["post", "featured"]

class ModeratorPostForm(BasePostForm):
    published_at = f.DateTimeField()
    layout = f.TextField(one_of=LAYOUTS)

```

::: warning
Deep hierarchies can become hard to debug. Limit to two (plus a base form) max levels and favor composition where possible (e.g., mixins for reusable snippets).
:::


## Using Forms

Forms are typically instantiated in a controller. When creating a form instance, you can either leave it empty or prepopulate it:

```python
form = MyForm()                      # 1
form = MyForm(request_data)          # 2
form = MyForm({}, object)            # 3
form = MyForm(request_data, object)  # 4
```

The `request_data` argument should be the data received from a previous HTML form submission. In every web framework, this is some kind of dictionary-like object that can have multiple values per key, for example `request.form` in Flask. <br>You can also use a dictionary of `key: [value1, value2, ...]` for testing.

The `object` argument should be data from a saved model instance, but you can also use a `key: value` dictionary instead.

In a web application, you will typically instantiate the form in four different ways, depending on whether you want to display the form for a new object, create it, edit it, or update it. Let's see it with an example.

This is our form:

```python
import formidable as f

class PostForm(f.Form):
    title = f.TextField()
    content = f.TextField(required=False)
```

#### 1. No request data or an empty one, and no object data.

```python
form = PostForm()
print(form.title.value)    # None
print(form.content.value)  # None
```

The fields values remain `None`.
Because the `title` field is required, this form will fail validation, but we can still use it for rendering.


#### 2. No object data, but some or all of the fields are in the request data.

```python
form = PostForm({"title": ["Hello world!"]})
print(form.title.value)    # "Hello world!"
print(form.content.value)  # None
```

This is the typical scenario when you have filled a form and submit it.
Because the `title` is the only required field, now that it has a non-empty value, the form will pass validation.


#### 3. There is object data and the request data is empty.

```python
form = PostForm(
  {},
  object={
    "title": "Hi",
    "content": "Lorem ipsum",
  }
)
print(form.title.value)    # "Hi"
print(form.content.value)  # "Lorem ipsum"
```

This is the typical scenario when you use a form to edit an object.


#### 4. Both request data and object data are present.

```python
form = PostForm(
  {
    "title": ["Hello world!"],
  },
  object={
    "title": "Hi",
    "content": "Lorem ipsum",
  }
)
print(form.title.value)    # "Hello world!"
print(form.content.value)  # "Lorem ipsum"
```

The value for `title` in the request data takes precedence over the one in the object.
This is the case when you use a form to edit an object and have submitted updated values.


## Form public API

### `is_valid` and `is_invalid` properties

These are properties that return whether the form is valid.

These properties have a side effect: they trigger validation of all fields and the form itself by calling the `.validate()` method and caching the result.

### `validate()`

You don't usually need to directly call this method, since the `is_valid`/`is_invalid` properties do it for you if needed.

The method triggers validation of each of its fields and, if there are no errors, it calls the [`after_validate`](#after_validate) method of the form, if one is defined.

Returns `True` or `False`, whether the form is valid after validation.

### `save(**extra)`

If the form is valid, this method will collect all the field values and:

a) If the form is not connected to an ORM model and it wasn't instantiate with an object, it will return the data as a dictionary.
b) If it *was* instantiate with an object, it will update and return the object (even if the "object" in question is a dictionary).
c) If it *wasn't* instantiate with an object, but it is connected to an ORM model, it will create a new object and return it.

```python
form = PostForm(
  {
    "title": ["Hello world!"],
  },
  object={
    "title": "Hi",
    "content": "Lorem ipsum",
  }
)
data = form.save()
print(data)
# {
#   "title": "Hello world!",
#   "content": "Lorem ipsum",
# }
```

In any case, this method can also take extra data that will be added before saving. This is useful to add things that should be included in a new object - like a `user_id` - but that you definitely don't want as an editable form field.

```python
product = form.save(user_id=123)
print(product.user_id)  # 123
```


## Form-level validation {id=after_validate}

If you add an `after_validate` method to the form, it will be called at the end of the validation process, after the individual field validations.

You can use to validate the relation between fields, for example in a update password scenario, or to modify the field values before saving.

```python {hl_lines="11"}
import formidable as f

class PasswordChangeForm(f.Form):
    password1 = f.TextField()
    password2 = f.TextField()

    def after_validate(self) -> bool:
        password1 = self.password1.value
        password2 = self.password2.value
        if password1 != password2:
            self.password2.error = "passwords_mismatch"
            return False
        return True

```

The method takes no arguments and must return `True` or `False`, indicating whether the form is valid after this final validation.

To indicate validation errors, set the `error` attribute of the individual fields, otherwise the user will not know *why* the form isn't valid.
