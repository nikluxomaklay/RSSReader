import os
from typing import List

from pydantic import BaseModel
from pydantic import PostgresDsn
from pydantic import computed_field

from helpers import load_env


class Config(BaseModel):
    CHECK_INTERVAL: int
    RSS_SOURCES: List[str]
    DEBUG: bool
    DB: DBConfig


class DBConfig(BaseModel):
    _driver: str = "postgresql+asyncpg"

    NAME: str
    HOST: str
    PORT: int
    USER: str
    PASSWORD: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> PostgresDsn:  # noqa
        return PostgresDsn(
            f"{self._driver}://"
            f"{self.USER}:{self.PASSWORD}"
            f"@{self.HOST}:{self.PORT}"
            f"/{self.NAME}",
        )


def init_config() -> Config:
    load_env()

    config = Config(
        CHECK_INTERVAL=os.getenv('RSS_CHECK_INTERVAL', 60),
        RSS_SOURCES=['https://www.cnews.ru/inc/rss/news.xml'],
        DEBUG=bool(os.getenv('DEBUG', 'False')),
        DB=DBConfig(
            NAME=os.getenv('RSS_DB_NAME', 'rss'),
            HOST=os.getenv('RSS_DB_HOST', 'localhost'),
            PORT=int(os.getenv('RSS_DB_PORT', '5432')),
            USER=os.getenv('RSS_DB_USER', ''),
            PASSWORD=os.getenv('RSS_DB_PASSWORD', ''),
        ),
    )

    return config
