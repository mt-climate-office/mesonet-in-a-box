from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import (
    autocommit_before_send_handler,
)
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
import os
from litestar import Litestar
from litestar.exceptions import ClientException
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from litestar.status_codes import HTTP_409_CONFLICT
from mesonet_utils import Config
from db.models import Base
from db import make_connection_string

from dotenv import load_dotenv
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    pass


CONFIG = Config.load(Config.file)

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


@asynccontextmanager
async def db_connection(app: Litestar) -> AsyncGenerator[None, None]:
    engine = getattr(app.state, "engine", None)
    if engine is None:
        raise ValueError(
            "No database engine defined for you app! Make sure environment variables pointing to the PG database are present."
        )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        await engine.dispose()


async def provide_transaction(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncSession, None]:
    try:
        async with db_session.begin():
            yield db_session

    except IntegrityError as exc:
        raise ClientException(
            status_code=HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


db_config = SQLAlchemyAsyncConfig(
    connection_string=make_connection_string(
        pg_username,
        pg_pw,
        "localhost",
        pg_db,
    ),
    metadata=Base.metadata,
    create_all=True,
    before_send_handler=autocommit_before_send_handler,
)
