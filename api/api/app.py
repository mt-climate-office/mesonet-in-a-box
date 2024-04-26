from __future__ import annotations

from config import db_config, provide_transaction
from litestar import Litestar, Router, post, get
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from sqlalchemy.ext.asyncio import AsyncSession
from db import models as db_models
import crud


@post("/stations")
async def post_station(
    data: db_models.Stations, transaction: AsyncSession
) -> db_models.Stations:
    transaction.add(data)
    return data


@get("/stations")  # , return_dto=models.StationReadDTO)
async def get_all_stations(transaction: AsyncSession) -> list[db_models.Stations]:
    data = await crud.get.query_all_stations(transaction)
    return data


@post("/elements")
async def post_element(
    data: db_models.Elements, transaction: AsyncSession
) -> db_models.Elements:
    transaction.add(data)
    return data


@post("/inventory")
async def post_inventory(
    data: db_models.Inventory, transaction: AsyncSession
) -> db_models.Inventory:
    transaction.add(data)
    return data


route_handlers = Router(
    path="/", route_handlers=[post_station, get_all_stations, post_element]
)
app = Litestar(
    route_handlers=[route_handlers],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
)
