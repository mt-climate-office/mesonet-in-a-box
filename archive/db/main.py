from mesonet_utils import Config  # type: ignore
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    from db.models import Base
    from db.make_db_tables import (
        make_connection_string,
        create_network_schema,
        create_data_schema,
    )

    CONFIG = Config.load(Config.file)

    token: str | None = CONFIG.airtable_token

    if CONFIG.directory is None:
        raise ValueError(
            "CONFIG directory cannot be None. Please rerun `mesonet configure`."
        )

    if CONFIG.env_file:
        load_dotenv(CONFIG.env_file)

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
