from __future__ import annotations

from config import db_config, provide_transaction
from litestar import Litestar, Router, post
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from sqlalchemy.ext.asyncio import AsyncSession
from db import models as db_models

# class StationController(Controller):
#     path = "/stations"

#     @get("/{station:str}/{latitude:float}/{longitude:float}", return_dto=models.StationWriteDTO)
#     async def get_stations(self, station: str, latitude: float, longitude: float) -> models.Station:
#         return models.Station(station=station, latitude=latitude, longitude=longitude, name='asdf', status='pending', date_installed="2024-01-01", elevation=234)


@post("/stations")
async def post_station(
    data: db_models.Stations, transaction: AsyncSession
) -> db_models.Stations:
    transaction.add(data)
    return data


@post("/elements")
async def post_element(
    data: db_models.Elements, transaction: AsyncSession
) -> db_models.Elements:
    transaction.add(data)
    return data


route_handlers = Router(path="/", route_handlers=[post_station, post_element])
app = Litestar(
    route_handlers=[route_handlers],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
)
