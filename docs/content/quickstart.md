---
title: Quickstart
---

## Install Formidable

Run the following command:

/// tab | Using "**pip**"

```bash
pip install formidable
```

///

/// tab | Using "**uv**"

```bash
uv add formidable
```

///


## Create a form


Create a new file in your project, which could be inside a `forms` folder.

```python {title="forms/team.py"}
import formidable as f

class TeamForm(f.Form):
    name = f.TextField()
    description = f.TextField(required=False)

```


## In the View

In your framework of choice, add it to your view. Here's how it looks:

```python {hl_lines="2 8"}
from flask import Flask, request, render_template
from .forms.team import TeamForm

app = Flask(__name__)

@app.route("/teams/new", methods=["GET"])
def index():
    form = TeamForm()
    return render_template("teams/new.html", form=form)

```


## In the Templates

Now let's look at the template side.

/// note | Render helpers
Formidable fields include some helper functions to write the HTML. They are very practical but completely optional. See for yourself:

*Without* helper functions:

```html+jinja {title="Manual HTML"}
<div class="form-field">
  <label for="{{ form.field.id }}">My label</label>
  <input type="text"
    id="{{ form.field.id }}"
    name="{{ form.field.name }}"
    value="{{ form.field.value }}"
  />
  {% if form.field.error -%}
    <span class="field-error">{{ form.field.error_message }}</span>
  {%- endif %}
</div>
```

*with* helper functions:

```html+jinja {title="With helpers"}
<div class="form-field">
  {{ form.field.label("My label") }}
  {{ form.field.text_input() }}
  {{ form.field.error_tag() }}
</div>
```
```

You can read more about these render methods in the [Fields page](/docs/fields/#render-methods).

///

Here is the `teams/new.html` template, which takes advantage of the helpers:

```html+jinja {title="teams/new.html"}
<form method="POST" action="/teams/create">
  <div class="field">
    {{ form.name.label("Name") }}
    {{ form.name.text_input() }}
    {{ form.name.error_tag() }}
  </div>

  <div class="field">
    {{ form.description.label("Description") }}
    {{ form.description.textarea() }}
    {{ form.description.error_tag() }}
  </div>

  <button type="submit">Create</button>
</form>
```

![Rendered form](/assets/images/quickstart-form-l.png){ .only-light .center }
![Rendered form](/assets/images/quickstart-form-d.png){ .only-dark .center }


## Validate the Form

When the user submits the form, let's process the information:


```python {hl_lines="3"}
@app.route("/teams/create", methods=["POST"])
def create():
    form = TeamForm(request.form)

    if form.is_invalid():  # or `if not form.is_valid`
        # There is an error, so re-render the form
        # with the submitted values and error messages
        return render_template("teams/new.html", form=form)

  # Form is valid, so we proceed
  data = form.save()
  create_team(**data)
  flash("Team created")
  return redirect(url_for("index"))

```

---

This is the basic pattern you will use for every form.
Keep reading for more customizations, field types, and additional details.