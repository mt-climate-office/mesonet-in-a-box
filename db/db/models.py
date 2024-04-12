from __future__ import annotations
import asyncio
import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Date
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, Str
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Stations(Base):
    __tablename__ = 'stations'
    __table_args__ = {'schema': "data"}  

    station: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(String, CheckConstraint("status IN ('pending', 'active', 'decommissioned', 'inactive')"))
    date_installed: Mapped[Date]
    nwsli_id: Mapped[str]
    sub_network: Mapped[str] = mapped_column(String, CheckConstraint("sub_network IN ('AgriMet', 'HydroMet')"))
    latitude: Mapped[float]
    longitude: Mapped[float]
    elevation: Mapped[float]
    report_mco: Mapped[bool]
    report_mesowest: Mapped[bool]
    ace_grid: Mapped[str]


class Elements(Base):
    __tablename__ = 'elements'
    __table_args__ = {"schema": "data"}

    element: Mapped[str] = mapped_column(primary_key=True)
    public: Mapped[bool]
    description: Mapped[str]
    description_short: Mapped[str]
    zentra_name: Mapped[str]
    ace_name: Mapped[str]
    base_units: Mapped[str]
    us_units: Mapped[str]
    usace_units: Mapped[str]

