---
title: Custom error messages
---

There are many reasons to want to edit the default error messages:

* You want to add new, more specific, error messages
* To make them fit with the "personality" of your application
* To translate them to the language of your users

For whatever reason you have, it's easy to do with Formidable forms.


## Messages format

When a form field has an error, there are three attributes related to that error in a field:

- `field.error` contains an error *code*, like "invalid";
- `field.error_args` is an optional dict of extra information related to the error (we will see more about this in moment); and
- `field.error_message` that is not actually an attribute but a *property* that uses the error code to search for a human-readable message in the `messages` dictionary of its parent form.

You can see the full (short) default dictionary of error messages in `formidable.errors.MESSAGES`. The dictionary uses the error codes as keys and the human-readable messages as values.

/// details | The full list of default messages

```python
MESSAGES = {
    "invalid": "Invalid value",
    "required": "Field is required",
    "one_of": "Must be one of {one_of}",
    "gt": "Must be greater than {gt}",
    "gte": "Must be greater or equal than {gte}",
    "lt": "Must be less than {lt}",
    "lte": "Must be less or equal than {lte}",
    "multiple_of": "Must multiple of {multiple_of}",
    "min_items": "Must have at least {min_length} items",
    "max_items": "Must have at most {max_length} items",
    "min_length": "Must have at least {min_length} characters",
    "max_length": "Must have at most {max_length} characters",
    "pattern": "Invalid format",
    "past_date": "Must be a date in the past",
    "future_date": "Must be a date in the future",
    "after_date": "Must be after {after_date}",
    "before_date": "Must be before {before_date}",
    "after_time": "Must be after {after_time}",
    "before_time": "Must be before {before_time}",
    "past_time": "Must be a time in the past",
    "future_time": "Must be a time in the future",
    "invalid_url": "Doesn't seem to be a valid URL",
    "invalid_email": "Doesn't seem to be a valid email address",
    "invalid_slug": "A valid “slug” can only have a-z letters, numbers, underscores, or hyphens",
}
```

///

They are generic by design, for example the message for a `"required"` error is `"Field is required"`, which can be good enough in some cases but it *feels* generic.

Some of the messages have placeholders, for example the `"min_length"` error - when a text is shorter than required - is `"Must have at least {min_length} characters"`. The `{min_length}` part will be replaced by a value of that name in the `field.error_args` dictionary. That way, the same message can be reused for different settings. You can do the same with your custom messages.


## Global messages

The default error messages can be updated/extended by declaring a base form with a `Meta` object containing a `messages` dictionary.

```python {hl_lines="5-8"}
import formidable as f

class BaseForm(f.Form):
  class Meta:
    messages = {
      "required": "Give me the value!"
      "lorem-ipsum": "I don't speak Latin"
    }

# later

class MyForm(BaseForm):
  # ...

```

The custom messages dictionary does not replace the default one, but *extends* it. In this example, the default "required" message is overwritten, and a new "lorem-ipsum" error is added, while the rest of the messages stay the same.


## Custom form messages

The custom messages dictionary can also be set when instantiating the form inside the view. You can, for example, translate the messages and use the translation that matches the user's language:

```python {hl_lines="4"}
form = MyForm(
  reqdata,
  objdata,
  messages=MESSAGES[user.locale]
)
```

/// note
The other way to translate your messages is to ignore the `messages` altogether, and instead use the error codes to do it in your templates. For example:

```html+jinja {hl_lines="9"}
<div class="form-field">
  {{ field.label("Label") }}
  {{ field.text_input() }}
  {% if field.error -%}
    <div class="field-error">{{ _(field.error) }}</div>
  {%- endif %}
</div>
```
///

## Custom field messages

Each field can also overwrite their own messages, to make them more specific, for example:

```python {hl_lines="5 8"}
import formidable as f

class PasswordChangeForm(f.Form):
    password1 = f.TextField(
        messages={"required": "Please write your new password"},
    )
    password2 = f.TextField(
        messages={"required": "Please repeat your new password"},
    )

```

## Raising custom errors

To raise an error in a filter or validator, you must use `raise ValueError(...)`.

The first argument will be the error code (`field.error`). Any other arguments will be collected in the `field.error_args` dictionary.

```python {hl_lines="5 10"}
import formidable as f

class NewPasswordForm(f.Form):
    password = f.TextField(
        messages={"must_contain": "The password must contain a '{char}' character"},
    )

    def validate_password(self, value):
        if "&" not in value:
            raise ValueError("must_contain", char="&")
        return value


print(form.password.error)  # "must_contain"
print(form.password.error_args)  # {"char": "&"}
```
