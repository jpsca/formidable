<div align="center">
  <h1><img alt="Formidable" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/formidable.png"></h1>
</div>
<p align="center">
  <img alt="coverage: 100%" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/coverage.svg">
  <img alt="license: MIT" src="https://raw.githubusercontent.com/jpsca/formidable/main/docs/license.svg">
</p>

### A small but powerful library for rendering and processing web forms

Documentation: [formidable.scaletti.dev](https://formidable.scaletti.dev/).


## Features

Formidable is small, modern, and handles the advanced scenarios you'll actually encounter in production applications.

- **Dynamic Nested Forms That Actually Work**

  Formidable's `NestedForms` field handles complex scenarios like users dynamically adding/removing subforms with proper deletion tracking, primary key management, and JavaScript integration out of the box.

- **Subforms**

  `FormField` elegantly handles nested data structures (JSON fields, one-to-one relationships).

- **Multiple ORM Support**

  Out-of-the-box integration with most ORMs: SQLAlchemy, Peewee, Pony ORM, Tortoise ORM, and SQLModel.

- **Translatable/customizable messages**

  Formidable's validation messages were designed to be easily translated or replaced.

- **Modern HTML-First Philosophy**

  Built for the modern era of HTMX, Turbo, and "HTML over the wire" patterns. Formidable embraces native HTML forms instead of fighting them, while still providing optional render helpers when you need them.

- **Render flexibility**

  Unlike other libraries where you're often stuck between manual HTML or opinionated widgets, Formidable lets you choose and mix and match as needed.


## Vision

By Internet standards, HTML forms are an ancient technology. At some point, we even forgot they existed, and for about 10 years, everyone was super excited about sending JSON over everything, all of the time.

But now we are realizing *"Oh, do you know what? HTML is actually really good!"*. It can be sent directly to a browser, and the browser can send form data back without any translation step. This native functionality is powerful and efficient.

However, in the world of Python web frameworks there is a problem: web forms had always been somewhat awkward. In fact, they were a big reason to use JavaScript in the first place. The existing libraries lack support for features like nested forms and/or are embedded in a particular framework.

That's why I built **Formidable**, a library that, although small, can handle all the advanced scenarios like subforms, dynamic nested forms, custom validators, translatable messages, integration with any ORM and template system, and more. I hope you enjoy it.


## Contributing Back

Find a bug? Head over to our [issue tracker](https://github.com/jpsca/formidable/issues) and we'll do our best to help. We love pull requests, too!
