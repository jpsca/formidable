---
title: Nested forms
---

![Under construction](/assets/images/construction.gif){.center title="Best viewed with Netscape Navigator :P"}

As your application grows, you may need to create more complex forms, beyond editing a single object. For example, when creating a `Person` you can allow the user to create multiple `Address` records (home, work, etc.) within the same form. When editing a `Person` record later, the user should be able to add, remove, or update addresses as well.

```python {hl_lines="10"}
import formidable as f
from .models import Address, Person

class AddressForm(f.Form):
    kind = f.TextField()
    street = f.TextField()
    # ...
    # fields for city, country, etc.

class PersonForm(f.Form):
    name = f.TextField()
    addresses = f.NestedForms(AddressForm)

```

# Nested forms in the template

```html+jinja
<form method="post">
  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">

  <label>Name</label>
  {{ form.name.render("Name") }}

  <fieldset>
    <legend>Addresses</legend>
    {% for address in form.addresses.forms %}
      <div>
        <div>{{ form.kind.render("Kind") }}</div>
        <div>{{ form.street.render("Street") }}<div>
        ...
      </div>
    {% endfor %}
  </fieldset>
</form>
```
