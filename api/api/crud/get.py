from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import models as db_models


async def query_all_stations(session: AsyncSession) -> list[db_models.Stations]:
    query = select(db_models.Stations)
    result = await session.execute(query)
    return result.scalars().all()
