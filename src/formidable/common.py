import typing as t


def get_pk(obj: t.Any, pk: str) -> t.Any:
    """
    Helper function to get the primary key from an object.
    """
    if isinstance(obj, dict):
        value = obj.get(pk, None)
    else:
        value = getattr(obj, pk, None)
    return str(value) if value else None
