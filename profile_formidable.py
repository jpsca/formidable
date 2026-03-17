"""
Profiling script for formidable.

Exercises the main code paths:
1. Form initialization (field discovery, cloning)
2. Request data parsing (flat dict -> nested)
3. Field setting & validation
4. NestedForms (multiple sub-forms)
5. SlugField (unicode normalization)
6. HTML rendering

Run:
    uv run python profile_formidable.py

Outputs:
    - Console: top 40 cumulative-time entries
    - profile_results.prof: full cProfile dump (for snakeviz, etc.)
"""

import cProfile
import pstats

import formidable as f


# -- Define realistic forms --------------------------------------------------

class AddressForm(f.Form):
    street = f.TextField()
    city = f.TextField()
    zip_code = f.TextField(required=False)
    country = f.TextField()


class ContactForm(f.Form):
    name = f.TextField()
    email = f.EmailField()
    phone = f.TextField(required=False)
    age = f.IntegerField(required=False)
    website = f.URLField(required=False)
    slug = f.SlugField(required=False)
    subscribe = f.BooleanField(required=False)
    notes = f.TextField(required=False)

    address = f.FormField(AddressForm)
    addresses = f.NestedForms(AddressForm, min_items=1, max_items=10)


# -- Build test data ----------------------------------------------------------

def make_flat_reqdata(n_addresses=5):
    """Simulate flat request data as it would arrive from an HTML form."""
    data = {
        "name": "José García-López",
        "email": "jose@example.com",
        "phone": "+1-555-0123",
        "age": "42",
        "website": "https://example.com/~jose",
        "slug": "Héllo Wörld! Ça va très bien, merci αβγδ",
        "subscribe": "on",
        "notes": "Some notes here",
        # FormField (single nested)
        "address[street]": "123 Main St",
        "address[city]": "Springfield",
        "address[zip_code]": "62704",
        "address[country]": "US",
    }
    # NestedForms (multiple nested)
    for i in range(n_addresses):
        prefix = f"addresses[{i}]"
        data[f"{prefix}[street]"] = f"{100 + i} Oak Avenue"
        data[f"{prefix}[city]"] = f"City {i}"
        data[f"{prefix}[zip_code]"] = f"{10000 + i}"
        data[f"{prefix}[country]"] = "US"

    return data


# -- Workloads ----------------------------------------------------------------

def workload_init_only(iterations=1000):
    """Measure form class instantiation (no data)."""
    for _ in range(iterations):
        ContactForm()


def workload_parse_set_validate(iterations=500):
    """Measure parse + set + validate cycle."""
    data = make_flat_reqdata(n_addresses=5)
    for _ in range(iterations):
        form = ContactForm(data)
        form.is_valid


def workload_large_nested(iterations=100):
    """Measure with many nested forms."""
    data = make_flat_reqdata(n_addresses=50)
    for _ in range(iterations):
        form = ContactForm(data)
        form.is_valid


def workload_render_html(iterations=500):
    """Measure HTML rendering helpers."""
    data = make_flat_reqdata(n_addresses=3)
    form = ContactForm(data)
    for _ in range(iterations):
        for field in form:
            field.label("Label")
            field.text_input()
            field.error_tag()


def workload_slug(iterations=2000):
    """Measure slug field processing."""
    from formidable.fields.slug import slugify
    texts = [
        "Héllo Wörld! Ça va très bien",
        "αβγδεζηθικλμνξοπρστυφχψω",
        "The Quick Brown Fox Jumps Over The Lazy Dog 123!@#$%",
        "ñoño año español café résumé naïve",
        "ა ბ გ დ ე ვ ზ თ ი კ ლ მ ნ ო პ",
    ]
    for _ in range(iterations):
        for text in texts:
            slugify(text)


def workload_parser(iterations=2000):
    """Measure raw parser performance."""
    from formidable.parser import parse
    data = make_flat_reqdata(n_addresses=20)
    for _ in range(iterations):
        parse(data)


def run_all():
    """Run all workloads together for a combined profile."""
    workload_init_only()
    workload_parse_set_validate()
    workload_large_nested()
    workload_render_html()
    workload_slug()
    workload_parser()


# -- Main --------------------------------------------------------------------

if __name__ == "__main__":
    print("Profiling formidable...")
    print("=" * 70)

    profiler = cProfile.Profile()
    profiler.enable()
    run_all()
    profiler.disable()

    # Save for visualization tools (snakeviz, pyprof2calltree, etc.)
    profiler.dump_stats("profile_results.prof")

    # Print summary
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")

    print("\n TOP 40 BY CUMULATIVE TIME")
    print("=" * 70)
    stats.print_stats(40)

    print("\n TOP 30 BY TOTAL (SELF) TIME")
    print("=" * 70)
    stats.sort_stats("tottime")
    stats.print_stats(30)

    print(f"\nFull profile saved to: profile_results.prof")
    print("Visualize with: uv run snakeviz profile_results.prof")
