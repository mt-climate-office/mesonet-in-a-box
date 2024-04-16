import airtable as at
import polars as pl
from mesonet_utils import Config
from pathlib import Path
import psycopg
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine.base import Engine
import os
from dotenv import load_dotenv
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
        conn.execute(text('CREATE SCHEMA IF NOT EXISTS data'))
        conn.commit()

def create_all_tables(engine):
    Base.metadata.create_all(engine)


        

if __name__ == "__main__":

    conn = make_connection_string(
        os.getenv("POSTGRES_USER"),
        os.getenv("POSTGRES_PASSWORD"),
        "localhost",
        os.getenv("POSTGRES_DB")
    )

    engine = create_engine(conn)
    create_all_tables(engine)