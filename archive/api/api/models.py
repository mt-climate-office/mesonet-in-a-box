from msgspec import Struct
from enum import Enum
from typing import TYPE_CHECKING
from datetime import date
from litestar.dto import MsgspecDTO, DTOConfig

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
    date_installed: date | None
    latitude: float
    longitude: float
    elevation: float
    deployments: list | None
    latitude_rounded: float | None = None
    longitude_rounded: float | None = None

    def __post_init__(self):
        self.latitude_rounded = round(self.latitude, 2)
        self.longitude_rounded = round(self.longitude, 2)
        # if isinstance(self.status, str):
        #     self.status = StationStatus(self.status)


class StationDTO(MsgspecDTO[Station]): ...


class StationReadDTO(MsgspecDTO[Station]):
    config = DTOConfig(
        exclude={"latitude", "longitude"},
        rename_fields={
            "latitude_rounded": "latitude",
            "longitude_rounded": "longitude",
        },
    )


class Test(Struct):
    dt: date | None
