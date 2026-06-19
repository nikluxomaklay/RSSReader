import json

from pydantic_core import to_jsonable_python


def db_json_serializer(*args: tuple, **kwargs: dict) -> str:
    """
    Encodes JSON in the same way that pydantic does for proper serialization.
    """
    return json.dumps(
        *args,
        default=to_jsonable_python,
        **kwargs,  # type: ignore
    )
