"""
# WriteaDoc Documentation

- `python docs.py run` to start a local server with live reload.
- `python docs.py build` to build the documentation for deployment.

"""
from writeadoc import Docs


pages = [
    "quickstart.md",
    "forms.md",
    "fields.md",
    "nested.md",
    {
        "title": "API",
        "closed": True,
        "pages": [
            "api/form.md",
            {
                "title": "Fields",
                "pages": [
                    "api/fields/text.md",
                    "api/fields/boolean.md",
                    "api/fields/integer.md",
                    "api/fields/float.md",
                    "api/fields/date.md",
                    "api/fields/datetime.md",
                    "api/fields/time.md",
                    "api/fields/slug.md",
                    "api/fields/email.md",
                    "api/fields/url.md",
                    "api/fields/list.md",
                    "api/fields/formfield.md",
                    "api/fields/formset.md",
                ]
            },
        ]
    }
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "Formidable",
        "description": "A small but powerful library for processing web forms",
        "base_url": "https://formidable.scaletti.dev",
        "lang": "en",
        "version": "0",
        "source_code": "https://github.com/jpsca/formidable/",
    },
)


if __name__ == "__main__":
    docs.cli()
