---
title: Fields
---

Fields are responsible for data conversion and validation.

## Field definitions

Fields are defined as members on a form in a declarative fashion:

```python
import formidable as f

class MyForm(f.Form):
    name = f.TextField(min_length=2, max_length=10)
    address = f.TextField(max_length=200, required=False)

```

At form instantiation time, a copy of each field is made with all the parameters specified in the definition. Each instance of the field keeps its own field data and settings.


## Custom filters/validators

A field "filter" is a function that transforms the input data before it is assigned as the field's value, but you can also use it for validation.

A field "validator" is a function that checks if the value can be saved, but you can also use it to transform the value before saving it.

Each field has its own internal filter and validators, but you can add custom ones by adding to the form methods named `filter_fieldname` and/or `validate_fieldname`.

<figure markdown="span">
<figcaption>Filter flow</figcaption>
![Filter flow](/assets/images/filter-flow.svg)
</figure>

<figure markdown="span">
<figcaption>Validate flow</figcaption>
![Validate flow](/assets/images/validate-flow.svg){.center}
</figure>

These methods receive the value the field has, and have to return a value back (the same or a transformed one).

```python
class MyForm(f.Form):
    name = f.TextField

    def filter_name(self, value):
        # Make any value lowercase
        return value.lower() if value else value

```

Remember to check if the value exists (is not `None`) before operating over it.

To indicate the value is not valid, they must raise a `ValueError` exception with the error code as the first argument

```python
class MyForm(f.Form):
    name = f.TextField

    def validate_name(self, value):
        # Validate it contains an "e"
        if "e" not in (value or ""):
            raise ValueError("invalid")

        return value

```

You can read more about error codes and messages in the ["Custom error messages"](/docs/messages/) page.
