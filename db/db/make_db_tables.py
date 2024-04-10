import airtable as at
import polars as pl
from mesonet_utils import Config
from pathlib import Path
import psycopg
from sqlalchemy import URL

CONFIG = Config.load(Config.file)
token: str = CONFIG.airtable_token
schema: Path = CONFIG.directory / "at_schema.json"

def connection(
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