---
title: Nested forms
---

As applications grow in complexity, you may need forms that go beyond editing a single object. For example, when creating a `Person` record, you might want users to add multiple `Address` records (home, work, etc.) within the same form. Later, when editing the `Person` record, users should be able to add, remove, or update any of those addresses.

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

    {% for address in form.addresses.forms -%}
    <div>
      {{ address.hidden_tags() }}
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
    {% endfor -%}
  </fieldset>
</form>
```

The `form.addresses` field creates a `forms` list containing `AddressForm` instances—one for each address.

If a person has no addresses, nothing is rendered.

A common pattern is to initialize the form with one or more empty nested forms, so users see at least one set of fields. Here's how to modify the above example:

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
      <input type="hidden" name="addresses[0][_destroy]" />
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
      <input type="hidden" name="addresses[1][_destroy]" />
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

The numbers in the names (`addresses[NUM]`) are not important and do not represent any order; what matters is that they are unique for each address.


Remember the `{{ address.hidden_tags() }}` from before? You must add this to *each nested form*, as it renders two hidden input tags necessary for editing existing objects.

* One hidden input tag, named `_id`, contains the primary key of the associated object; and
* Another named `_destroy`, which is relevant when the user can add or remove forms and, if filled, indicates that the associated object should be deleted.


::: warning | Is sending ids safe?
Don't worry about malicious users editing the hidden `_id` field. The value is ignored if it does not belong to one of the objects used to instantiate the form, so users cannot update objects they are not authorized to modify.
:::

In the example above, the `_id` hidden inputs weren't added because the forms were empty, and neither were the `_destroy` ones because we hadn't allowed removing associated objects.


## Removing Associated Objects

You can allow users to delete associated objects by passing `allow_delete=True` to the `NestedForms` field.

```python {hl_lines="10"}
class PersonForm(f.Form):
    class Meta:
        orm_cls = Person

    name = f.TextField()
    addresses = f.NestedForms(AddressForm, allow_delete=True)

```

If the form data contains the key `_destroy` with a non-empty value, the object will be deleted.


## Dynamic nested forms

So far, we've shown a fixed number of nested forms, but it's common to allow users to add or remove forms in the browser. This type of client-side manipulation requires JavaScript, but the neat part is you don't have to write it yourself.

Formidable forms use the same (or similar) naming conventions as Ruby on Rails, so there are already JavaScript libraries written for this task.

For this example, we are going to use a modified version of ["Stimulus Rails Nested Form"](https://www.stimulus-components.com/docs/stimulus-rails-nested-form/){target=_blank} script that depends on the [Stimulus JavaScript library](https://stimulus.hotwired.dev/){target=_blank}.

This is the recommended way to do it and, in fact, it's [included within](https://github.com/jpsca/formidable/blob/main/src/formidable/nested-form-controller.js){target=_blank} the Formidable source code repo.

We are going to build this simple to-do list you can see here (it's live, try it!):

<form
  id="nested-form-demo"
  method="post"
  data-controller="nested-form"
  novalidate
>
  <h2>Nested Forms</h2>

  <div class="nested-form-wrapper">
    <label for="f2732e072d9634fb8bf3195ef7f1d436c">Your todo</label>
    <div class="field">
      <input type="text" id="f2732e072d9634fb8bf3195ef7f1d436c" name="todo[0][description]" value="Pet the cat" required />
      <button type="button" data-action="nested-form#remove"
        title="Remove todo">&times;</button>
    </div>
    <input type="hidden" name="todo[0][_destroy]" />
  </div>

  <template data-nested-form-target="template">
    <div class="nested-form-wrapper">
      <label for="ftemp1">New Todo</label>
      <div class="field">
        <input type="text" id="ftemp1" name="todo[NEW_RECORD][description]" required />
        <button type="button" data-action="nested-form#remove"
          title="Remove todo">&times;</button>
      </div>
    </div>
  </template>

  <div id="nested-form-target" data-nested-form-target="target"></div>

  <div class="actions">
    <button type="button" data-action="nested-form#add">Add todo</button>
  </div>
</form>

### 1. Add Stimulus.js to your project

Download [`stimulus.js` from here](https://unpkg.com/@hotwired/stimulus/dist/stimulus.js) and save it to your project, for example to `static/js/stimulus.js`. Do the same for the [`nested-form-controller.js` file](https://raw.githubusercontent.com/jpsca/formidable/refs/heads/main/src/formidable/nested-form-controller.js).

Then, add this to the header of your base template:

```html {hk_lines="4-8"}
<html>
  <head>
    ...
    <script type="module">
      import { Application } from "/static/js/stimulus.js";
      window.Stimulus = Application.start();
    </script>
    <script type="module" src="/static/js/nested-form-controller.js"></script>
  </head>
  ...
```

### 2. Create your forms

As before, let's create our forms:

```python {title="forms/todo.py"}
import formidable as f

class TodoForm(f.Form):
    description = f.TextField(required=True)

class TodoListForm(f.Form):
    todo = f.NestedForms(TodoForm, allow_delete=True)
```

... and a template. I'm using a macro to render the `TodoForm` (because later we are going to need to render it more than once:

```html+jinja
{% macro render_todo(form, label) -%}
<div>
  {{ form.description.label(label) }}
  {{ form.description.text_input() }}
  {{ form.description.error_tag() }}
  {{ form.hidden_tags() }}
</div>
{%- endmacro %}

<form method="post" novalidate>
  <h2>Nested Forms</h2>
  {% for todo_form in form.todo.forms %}
  {{ render_todo(todo_form, "Your todo") }}
  {% endfor %}
</form>
```

This is still a static version of the nested forms, so let's add the rest.

### 3. Connect the form to the Stimulus "controller"

Add `data-controller="nested-form"` to the form tag or to a wrapper tag:

```html+jinja
...
<form method="post" data-controller="nested-form" novalidate>
...

```

### 4. Add a `nested-form-wrapper` class to the nested form

```html+jinja {hl_lines="2"}
{% macro render_todo(form, label) -%}
<div class="nested-form-wrapper">
  {{ form.description.label(label) }}
  ...
</div>
{%- endmacro %}
...
```

### 5. Add a "Remove todo" button

```html+jinja {hl_lines="6-7"}
{% macro render_todo(form, label) -%}
<div class="nested-form-wrapper">
  {{ form.description.label(label) }}
  <div class="field">
    {{ form.description.text_input() }}
    <button type="button" data-action="nested-form#remove"
      title="Remove todo">&times;</button>
  </div>
  {{ form.description.error_tag() }}
  {{ form.hidden_tags() }}
</div>
{%- endmacro %}
...
```

### 6. Add a template for the nested form

The JS script needs something to clone so it can add a new nested form, let's add a template so it can do it (by literally using a `template` HTML tag):

```html+jinja {hl_lines="9-11"}
...
<form method="post" data-controller="nested-form" novalidate>
  <h2>Nested Forms</h2>

  {% for todo_form in form.todo.forms %}
  {{ render_todo(todo_form, "Your todo") }}
  {% endfor %}

  <template data-nested-form-target="template">
    {{ render_todo(form.todo.empty_form, "New Todo") }}
  </template>
</form>
```

**Note that we call the macro using `form.todo.empty_form`**. This is a special attribute of a `NestedForms` field that generates an empty instance of a nested form, excatly for using it for this cases.

It's important to put it *inside* the element with the `data-controller="nested-form"` attribute (the form tag in our example).

### 7. Choose where to insert the new nested forms

This must also be *inside* the element with the `data-controller="nested-form"` attribute. Let's add it to the bottom of the form tag.

```html+jinja {hl_lines="2"}
  ...
  <div data-nested-form-target="target"></div>
</form>
```

### 8. Action!

Finally, we need something to trigger the insertion of a new nested form, let's add a button to do just that:

```html+jinja {hl_lines="3"}
  ...
  <div class="actions">
    <button type="button" data-action="nested-form#add">Add todo</button>
  </div>
</form>
```

### 9. Final version

That's it, the final version of the template should look like this:

```html+jinja
{% macro render_todo(form, label) -%}
<div class="nested-form-wrapper">
  {{ form.description.label(label) }}
  <div class="field">
    {{ form.description.text_input() }}
    <button type="button" data-action="nested-form#remove"
      title="Remove todo">&times;</button>
  </div>
  {{ form.description.error_tag() }}
  {{ form.hidden_tags() }}
</div>
{%- endmacro %}

<form method="post" data-controller="nested-form" novalidate>
  <h2>Nested Forms</h2>

  {% for todo_form in form.todo.forms %}
  {{ render_todo(todo_form, "Your todo") }}
  {% endfor %}

  <template data-nested-form-target="template">
    {{ render_todo(form.todo.empty_form, "New Todo") }}
  </template>
  <div data-nested-form-target="target"></div>

  <div class="actions">
    <button type="button" data-action="nested-form#add">Add todo</button>
  </div>
</form>
```
