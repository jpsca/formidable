import typing as t


PK_NAME = "_id"
# Instead of "_delete", we use "_destroy" to be compatible with Rails forms.
DELETED_NAME = "_destroy"


def get_pk(obj: t.Any, pk: str) -> t.Any:
    """
    Helper function to get the primary key from an object.
    """
    if isinstance(obj, dict):
        value = obj.get(pk, None)
    else:
        value = getattr(obj, pk, None)
    return str(value) if value else None
