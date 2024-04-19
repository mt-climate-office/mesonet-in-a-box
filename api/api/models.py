from msgspec import Struct
from enum import Enum
from typing import TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    pass


class StationStatus(Enum):
    pending: str = "pending"
    active: str = "active"
    decommissioned: str = "decommissioned"
    inactive: str = "inactive"


class Station(Struct):
    station: str
    name: str
    status: StationStatus
    date_installed: date
    latitude: float
    longitude: float
    elevation: float


# class StationRepository(SQLAlchemyAsyncRepository[models.Stations]):
#     model_type = models.Stations

# async def provide_station_repo(db_session: AsyncSession) -> StationRepository:
#     return StationRepository(session=db_session)

# async def provide_station_deployments_repo(db_session: AsyncSession) -> StationRepository:
#     return StationRepository(
#         statement=select(models.Stations).options(selectinload(models.Stations.components))
#     )
