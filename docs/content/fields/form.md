---
title: FormField
---

::: api formidable.FormField
:show_members: false
:::
----

This is a form field that contains another form as its value. For example:

```python
import formidable as f

class SettingsForm(f.Form):
    locale = f.TextField(default="en_us")
    timezone = f.TextField(default="utc")
    email_notifications = f.BooleanField(default=False)


class Profile(f.Form):
    name = f.TextField(required=False)
    settings = f.FormField(SettingsForm)

```

![Rendered form](/assets/images/form.png){.invert}

To the user, this will probably look as part of the same form, why bother then? Well, this field isn't about showing the form, it's about how the data is saved.

When saving a form with a `FormField`, the contents of it comes encapsulated in their own object or dictionary:

```python
print(form.save())

{
  "name": "My name",
  "settings": {
    "locale": "en_us"
    "timezone": "utc",
    "email_notifications": True,
  },
}
```

This field is useful when you want to store those group of fields separated, for example:

In a different model with a one-to-one relationship to the main model

```python
class Settings(Model):
    locale = Text()
    timezone = Text()
    email_notifications = Bool()

class Profile(Model):
    name = Text()
    settings = ForeignKey(Settings, backref="profile", lazy_load=True)

```

\- or -

In a JSON field, that you want to validate before saving.

```python
class Profile(Model):
    name = Text()
    settings = JSON()
```
