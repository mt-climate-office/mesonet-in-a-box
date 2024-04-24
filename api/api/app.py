from __future__ import annotations

from config import db_config, provide_transaction
from msgspec import Struct
from litestar import Litestar, Router, post
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from sqlalchemy.ext.asyncio import AsyncSession
from db import models as db_models


class Test(Struct):
    info: str


# class StationController(Controller):
#     path = "/stations"

#     @get("/{station:str}/{latitude:float}/{longitude:float}", return_dto=models.StationWriteDTO)
#     async def get_stations(self, station: str, latitude: float, longitude: float) -> models.Station:
#         return models.Station(station=station, latitude=latitude, longitude=longitude, name='asdf', status='pending', date_installed="2024-01-01", elevation=234)


@post("/stations/")
async def post_station(
    data: db_models.Stations, transaction: AsyncSession
) -> db_models.Stations:
    print(type(data))
    # db_models.Stations()
    transaction.add(data)
    return data


station_handler = Router(path="/", route_handlers=[post_station])
app = Litestar(
    route_handlers=[station_handler],
    dependencies={"transaction": provide_transaction},
    plugins=[SQLAlchemyPlugin(db_config)],
)
