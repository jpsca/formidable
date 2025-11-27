<div align="center">
  <h1><img alt="Formidable" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/formidable.png"></h1>
</div>
<p align="center">
  <img alt="coverage: 100%" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/coverage.svg">
  <img alt="license: MIT" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/license.svg">
</p>

### A small but powerful library for rendering and processing web forms


## Features

- Dynamic nested forms
- Subforms
- Translatable/customizable messages
- Custom filters and validators
- Integration with any ORM and template system


## Vision

By Internet standards, HTML forms are an ancient technology. At some point, we even forgot they existed, and for about 10 years, everyone was super excited about sending JSON over everything, all of the time.

But now we are realizing *"Oh, do you know what? HTML is actually really good!" It can be sent directly to a browser, and the browser can send form data back without any translation step. This native functionality is powerful and efficient.

However, in the world of Python web frameworks there is a problem: web forms had always been somewhat awkward. In fact, they were a big reason to use JavaScript in the first place. The existing libraries lack support for features like nested forms and/or are embedded in a particular framework.

That's why I built **Formidable**, a library that, although small, can handle all the advanced scenarios like subforms, dynamic nested forms, custom validators, translatable messages, integration with any ORM and template system, and more. I hope you enjoy it.

## Why not WTForms?

WTForms has served the Python community well, but it shows its age:

- Nested forms are awkward with `FieldList`. Formidable's `NestedForms` handles dynamic add/remove scenarios elegantly.
- Limited ORM support. Formidable supports Peewee, Pony, Tortoise, SQLAlchemy, and SQLModel out of the box.
- All-or-nothing rendering. Formidable lets you use render helpers or write plain HTML
- Poor internationalization support. Formidable validation messages were designed to be easily translated or replaced.
- Verbose API. More boilerplate, less clarity

Formidable is small, modern, and handles the advanced scenarios you'll actually encounter in production applications.

## Contributing Back

Find a bug? Head over to our issue tracker and we'll do our best to help. We love pull requests, too!
