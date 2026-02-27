import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from config import init_config
from db.utils import db_json_serializer
from rss_reader import RSSReader


async def main():
    config = init_config()
    engine = create_async_engine(
        url=str(config.DB.DATABASE_URL),
        echo="debug" if config.DEBUG else None,
        json_serializer=db_json_serializer,
    )
    await RSSReader(
        config=config,
        session_factory=async_sessionmaker(autocommit=False, bind=engine),
    ).run()

if __name__ == "__main__":
    asyncio.run(main())
