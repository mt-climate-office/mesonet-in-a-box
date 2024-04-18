from mesonet_utils import Config  # type: ignore
from pathlib import Path
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
from models import Base

CONFIG = Config.load(Config.file)

token: str | None = CONFIG.airtable_token

if CONFIG.directory is None:
    raise ValueError(
        "CONFIG directory cannot be None. Please rerun `mesonet configure`."
    )
schema: Path = CONFIG.directory / "at_schema.json"

if CONFIG.env_file:
    load_dotenv(CONFIG.env_file)


def make_connection_string(
    username: str,
    password: str,
    host: str,
    database: str,
) -> URL:
    return URL.create(
        "postgresql+psycopg",
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


if __name__ == "__main__":
    pg_username = os.getenv("POSTGRES_USER")
    if pg_username is None:
        raise ValueError("POSTGRES_USER environment variable couldn't be found.")

    pg_pw = os.getenv("POSTGRES_PASSWORD")
    if pg_pw is None:
        raise ValueError("POSTGRES_PASSWORD environment variable couldn't be found.")

    pg_db = os.getenv("POSTGRES_DB")
    if pg_db is None:
        raise ValueError("POSTGRES_DB environment variable couldn't be found.")

    conn = make_connection_string(
        pg_username,
        pg_pw,
        "localhost",
        pg_db,
    )

    engine = create_engine(conn)

    create_network_schema(engine)
    create_data_schema(engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
