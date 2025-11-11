---
title: Nested forms
---

![Under construction](/assets/images/construction.gif){.center title="Best viewed with Netscape Navigator 6.0"}

----

As applications grow in complexity, you may need forms that go beyond editing a single object. For example, when creating a `Person` record, you might want users to add multiple `Address` records (home, work, etc.) within the same form. Later, when editing that `Person` record, users should be able to add, remove, or update any of those addresses.

```python {hl_lines="10"}
import formidable as f
from .models import Address, Person

class AddressForm(f.Form):
    class Meta:
        orm_cls = Address

    kind = f.TextField()
    street = f.TextField()
    # fields for city, country, etc.

class PersonForm(f.Form):
    class Meta:
        orm_cls = Person

    name = f.TextField()
    addresses = f.NestedForms(AddressForm)

```

## Rendering nested forms

```html+jinja
<form method="post">
  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">

  {{ form.name.label("Name") }}
  {{ form.name.text_input() }}
  {{ form.name.error_tag() }}

  <fieldset>
    <legend>Addresses</legend>

    {% for address in form.addresses.forms %}
    <div>
      <div class="field">
        {{ address.kind.label("Kind") }}
        {{ address.kind.text_input() }}
        {{ address.kind.error_tag() }}
      </div>

      <div class="field">
        {{ address.street.label("Street") }}
        {{ address.street.text_input() }}
        {{ address.street.error_tag() }}
      </div>
    </div>
    {% endfor %}
  </fieldset>
</form>
```

The `form.addresses` field creates a `forms` list containing `AddressForm` instances, one for each address.
If a person has no addresses, nothing will be rendered.

A common pattern is to initialize the form with one or more empty nested forms so that users see at least one set of fields. Here's how to modify the above example:

```python {hl_lines="4"}
@app.route("/person/new/")
def new():
    form = PersonForm()
    form.addresses.build(2)
    return render_template("person/new.html", form=form)

```

Will output the following HTML:

```html
<form method="post">
  <input type="hidden" name="_csrf_token" value="...">

  <label for="f67b...">Name</label>
  <input type="text" id="f67b..." name="name" required />

  <fieldset>
    <legend>Addresses</legend>

    <div>
      <div class="field">
        <label for="f7f7...">Kind</label>
        <input type="text" id="f7f7..." name="addresses[0][kind]" required />
      </div>
      <div class="field">
        <label for="ff85...">Street</label>
        <input type="text" id="ff85..." name="addresses[0][street]" required />
      </div>
    </div>

    <div>
      <div class="field">
        <label for="f725...">Kind</label>
        <input type="text" id="f725..." name="addresses[1][kind]" required />
      </div>
      <div class="field">
        <label for="ff84...">Street</label>
        <input type="text" id="ff84..." name="addresses[1][street]" required />
      </div>
    </div>

  </fieldset>
</form>
```


The numbers in the names (`addresses[NUM]`) are not important and do not represent any order; it only matters that they are unique for each address.

/// warning | Keep reading
We'll discuss later how users can dynamically add and remove nested forms as needed, but first let's understand how it works with these two fixed nested forms.
///


## Updating objects


There is one important difference when using nested forms to update existing objects: you must add a `{{ nestedform.hidden_tags }}` declaration *to each nested form* (you can also add it to empty nested forms, but it will have no effect).

```html+jinja {hl_lines="13"}
<form method="post">
  <input type="hidden" name="_csrf_token" value="{{ csrf_token() }}">

  {{ form.name.label("Name") }}
  {{ form.name.text_input() }}
  {{ form.name.error_tag() }}

  <fieldset>
    <legend>Addresses</legend>

    {% for address in form.addresses.forms %}
    <div>
      {{ address.hidden_tags }}

      <div class="field">
        {{ address.kind.label("Kind") }}
        {{ address.kind.text_input() }}
        {{ address.kind.error_tag() }}
      </div>

      <div class="field">
        {{ address.street.label("Street") }}
        {{ address.street.text_input() }}
        {{ address.street.error_tag() }}
      </div>
    </div>
    {% endfor %}
  </fieldset>
</form>
```


The `hidden_tags` property returns two hidden input tags: one named `_destroy`, which, if filled, indicates that the associated object should be deleted; and another named `_id`, which contains the primary key of the associated object.

/// warning | Is that safe?
Don't worry about malicious users editing the hidden `_id` field. The value is ignored if it does not belong to one of the objects used to instantiate the form, so a user cannot update an object they are not authorized to modify.
///

----

![Under construction](/assets/images/construction.gif){.center title="Best viewed with Internet Explorer 5.0"}
