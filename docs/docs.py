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
    {
        "title": "Included fields",
        "pages": [
            {
                "title": "Basic fields",
                "pages": [
                    "fields/text.md",
                    "fields/boolean.md",
                    "fields/integer.md",
                    "fields/float.md",
                    "fields/file.md",
                    "fields/list.md",
                ]
            },
            {
                "title": "Date fields",
                "pages": [
                    "fields/date.md",
                    "fields/datetime.md",
                    "fields/time.md",
                ]
            },
            {
                "title": "Convenience fields",
                "pages": [
                    "fields/email.md",
                    "fields/url.md",
                    "fields/slug.md",
                ]
            },
            {
                "title": "Form fields",
                "pages": [
                    "fields/form.md",
                    "fields/nested.md",
                ]
            },
        ]
    },
    "nested.md",
    "orm.md",
    "messages.md",
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
