"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import re
import typing as t


# Regex pattern for valid Python variable names with Unicode support
# (but NOT supplementary planes, like emojis).
re_name = r"[_a-zA-Z\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF][_a-zA-Z0-9\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF\.]*"
re_key = rf"{re_name}|\[{re_name}\]|\[[0-9]+\]|\[\]"
rx_key = re.compile(re_key)


def parse_key(key: str) -> list[str | int | None]:
    key = key.strip()
    if not key or key.startswith("["):
        return []

    parts = rx_key.findall(key)
    parsed = []
    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            inner = part[1:-1].strip()
            if not inner:  # empty brackets
                parsed.append(None)
            else:
                parsed.append(inner)
        else:
            parsed.append(part)
    return parsed


def insert(
    parsed_key: list[str | int | None], value: t.Any, target: dict[str, t.Any]
) -> None:
    last_index = len(parsed_key) - 1
    ref: dict[str, t.Any] | list[t.Any] = target

    for i, part in enumerate(parsed_key):
        is_last = i == last_index
        next_part = parsed_key[i + 1] if not is_last else None

        if part is None:  # append a list element
            assert isinstance(ref, list)
            if is_last:
                ref.append(value)
            else:
                new_elem = {} if isinstance(next_part, str) else []
                ref.append(new_elem)
                ref = new_elem

        else:  # dict key
            if is_last:
                assert isinstance(ref, dict)
                ref[part] = value  # type: ignore
            else:
                if part not in ref or not isinstance(ref[part], (dict, list)):  # type: ignore
                    ref[part] = {} if isinstance(next_part, str) else []  # type: ignore
                ref = ref[part]  # type: ignore


def get_items(reqdata: t.Any):  #  pragma: no cover
    """Return an iterable of (key, values) pairs from a dict-like object.
    Works with the most common web frameworks' request data structures.
    """
    # e.g.: Starlette MultiDict (FastAPI)
    if hasattr(reqdata, "multi_items"):
        return reqdata.multi_items()

    # e.g.: Django QueryDict
    if hasattr(reqdata, "lists"):
        return reqdata.lists()

    # e.g.: Werkzeug MultiDict (Flask)
    if hasattr(reqdata, "iterlists"):
        return reqdata.iterlists()

    # e.g.: Bottle MultiDict
    if hasattr(reqdata, "allitems"):
        return reqdata.allitems()

    # e.g.: plain dict or similar
    if hasattr(reqdata, "items"):
        return reqdata.items()

    raise TypeError(f"Unsupported type for reqdata: {type(reqdata)}")


def parse(reqdata: t.Any) -> dict[str, t.Any]:
    """Parse a flat dict-like object into a nested structure based on keys.

    Args:
        reqdata:
            A dict-like object containing the request data, where keys
            may include nested structures (e.g., "user[name]", "user[age]").

    Returns:
        A nested dictionary where keys are parsed into a hierarchy based on
        the structure of the original keys. For example, "user[name]" becomes
        {"user": {"name": value}}.

    """
    if not reqdata:
        return {}

    result = {}
    for key, values in get_items(reqdata):
        if not isinstance(values, list) or not values:
            values = [values]
        parsed_key = parse_key(key)
        for value in values:
            insert(parsed_key, value, result)

    return result
