from sqlalchemy import URL, text
from sqlalchemy.engine.base import Engine


def make_connection_string(
    username: str,
    password: str,
    host: str,
    database: str,
) -> URL:
    return URL.create(
        "postgresql+asyncpg",
        username=username,
        password=password,
        host=host,
        database=database,
    )


def create_data_schema(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS data"))
        conn.commit()


def create_network_schema(engine: Engine) -> None:
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS network"))
        conn.commit()
