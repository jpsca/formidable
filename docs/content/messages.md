---
title: Custom error messages
---

There are several common reasons to customize error messages:

* Adding new, more specific error messages
* Matching your application's tone and personality
* Translating messages to your users' language

Formidable makes it easy to customize error messages for any of these purposes.


## Messages format

When a form field has an error, it exposes three error-related attributes:

- `field.error`: Contains an error *code*, such as "invalid"
- `field.error_args`: An optional dictionary of extra information related to the error (explained in detail below)
- `field.error_message`: A *property* that uses the error code to retrieve a human-readable message from the form's `messages` dictionary

You can see the full (short) default dictionary of error messages in `formidable.errors.MESSAGES`. The dictionary uses the error codes as keys and the human-readable messages as values.

::: note | The full list of default messages
:open: false

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
:::

These messages are intentionally generic. For example, the `"required"` error message is simply `"Field is required"` - functional but generic.

Some messages include placeholders. For example, the `"min_length"` error message (used when text is shorter than required) is `"Must have at least {min_length} characters"`. The `{min_length}` placeholder is replaced with the corresponding value from the `field.error_args` dictionary. This system allows messages to be reused with different parameters, and you can use the same approach in your custom messages.


## Global messages

The default error messages can be updated/extended by declaring a base form with a `Meta` object containing a `messages` dictionary.

```python {hl_lines="5-8"}
import formidable as f

class BaseForm(f.Form):
  class Meta:
    messages = {
      "required": "Give me the value!",
      "lorem-ipsum": "I don't speak Latin"
    }

# later

class MyForm(BaseForm):
  # ...

```

The custom messages dictionary extends rather than replaces the default one. In this example, the default "required" message is overwritten and a new "lorem-ipsum" error is added, while all other default messages remain unchanged.


## Custom form messages

The custom messages dictionary can also be set when instantiating the form inside the view. You can, for example, translate the messages and use the translation that matches the user's language:

```python {hl_lines="4"}
form = MyForm(
  reqdata,
  objdata,
  messages=MESSAGES[user.locale]
)
```

::: note
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
:::

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
