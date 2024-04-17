from mesonet_utils import Config
from pathlib import Path
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import DeclarativeBase
from models import Base

CONFIG = Config.load(Config.file)
token: str = CONFIG.airtable_token
schema: Path = CONFIG.directory / "at_schema.json"

if CONFIG.env_file.exists():
    load_dotenv(CONFIG.env_file)

def make_connection_string(
    username: str,
    password: str,
    host: str,
    database: str,
) -> str:
    return URL.create(
        "postgresql+psycopg",
        username=username,
        password=password,
        host=host,
        database=database,
    )


def create_data_schema(engine: Engine):
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS data"))
        conn.commit()


def create_network_schema(engine: Engine):
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS network"))
        conn.commit()


def create_base_tables(engine: Engine, base: DeclarativeBase):
    base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    conn = make_connection_string(
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        "localhost",
        os.getenv("POSTGRES_DB"),
    )

    engine = create_engine(conn)

    create_network_schema(engine)
    create_data_schema(engine)
    Base.metadata.drop_all(bind=engine)
    print('did this')
    create_base_tables(engine, base=Base)

