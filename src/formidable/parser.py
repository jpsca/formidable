"""
Formidable | Copyright (c) 2025 Juan-Pablo Scaletti
"""

import typing as t


_parse_key_cache: dict[str, list[str | None]] = {}


def parse_key(key: str) -> list[str | None]:
    cached = _parse_key_cache.get(key)
    if cached is not None:
        return cached

    result = _parse_key_impl(key)
    _parse_key_cache[key] = result
    return result


def _parse_key_impl(key: str) -> list[str | None]:
    # Single-pass parser: avoids split + rstrip + strip per segment
    s = key.strip()
    if not s or s[0] == "[":
        return []

    bracket = s.find("[")
    if bracket == -1:
        return [s]

    parts: list[str | None] = [s[:bracket]]
    pos = bracket
    end = len(s)

    while pos < end:
        # pos should be at '['
        close = s.find("]", pos + 1)
        if close == -1:
            # Malformed: treat rest as part name
            inner = s[pos + 1:]
            parts.append(inner if inner else None)
            break
        inner = s[pos + 1:close]
        parts.append(inner if inner else None)
        pos = close + 1

    return parts


def insert(
    parsed_key: list[str | None], value: t.Any, target: dict[str, t.Any]
) -> None:
    last_index = len(parsed_key) - 1
    ref: dict[str, t.Any] | list[t.Any] = target

    for i, part in enumerate(parsed_key):
        if i == last_index:
            if part is None:
                ref.append(value)  # type: ignore
            else:
                ref[part] = value  # type: ignore
        elif part is None:
            new_elem = {} if parsed_key[i + 1] is not None else []
            ref.append(new_elem)  # type: ignore
            ref = new_elem
        else:
            child = ref.get(part)  # type: ignore
            if type(child) is not dict and type(child) is not list:
                child = {} if parsed_key[i + 1] is not None else []
                ref[part] = child  # type: ignore
            ref = child


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

    result: dict[str, t.Any] = {}

    # Fast path for plain dicts (most common case)
    if type(reqdata) is dict:
        for key, value in reqdata.items():
            parsed_key = parse_key(key)
            if type(value) is list:
                for v in value:
                    insert(parsed_key, v, result)
            else:
                insert(parsed_key, value, result)
    else:
        items = get_items(reqdata)
        for key, values in items:
            if not isinstance(values, list) or not values:
                values = [values]
            parsed_key = parse_key(key)
            for value in values:
                insert(parsed_key, value, result)

    return result
