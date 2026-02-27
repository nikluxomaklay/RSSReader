from config import DBConfig
from config import init_config


class AlembicConfig(DBConfig):
    _driver: str = 'postgresql'


def init_alembic_config():
    config = init_config()
    return AlembicConfig(
        NAME=config.DB.NAME,
        HOST=config.DB.HOST,
        PORT=config.DB.PORT,
        USER=config.DB.USER,
        PASSWORD=config.DB.PASSWORD,
    )


alembic_config = init_alembic_config()
