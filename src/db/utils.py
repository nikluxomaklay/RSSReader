import json
from typing import AsyncIterator

from pydantic_core import to_jsonable_python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker


async def get_session(engine) -> AsyncIterator[AsyncSession]:
    session_maker = async_sessionmaker(autocommit=False, bind=engine)
    async with session_maker() as session:
        yield session


def db_json_serializer(*args: tuple, **kwargs: dict) -> str:
    """
    Encodes JSON in the same way that pydantic does for proper serialization.
    """
    return json.dumps(
        *args,
        default=to_jsonable_python,
        **kwargs,  # type: ignore
    )
