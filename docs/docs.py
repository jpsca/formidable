"""
# WriteaDoc Documentation

- `python docs.py run` to start a local server with live reload.
- `python docs.py build` to build the documentation for deployment.

"""
from writeadoc import Docs


pages = [
    "quickstart.md",
]

docs = Docs(
    __file__,
    pages=pages,
    site={
        "name": "Formidable",
        "description": "A simple but powerful library for processing web forms",
        "base_url": "https://formidable.scaletti.dev",
        "lang": "en",
        "version": "0.8",
        "source_code": "https://github.com/jpsca/formidable/",
    },
)


if __name__ == "__main__":
    docs.cli()
