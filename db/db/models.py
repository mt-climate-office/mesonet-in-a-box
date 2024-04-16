from __future__ import annotations
import asyncio
import datetime
from datetime import date
from typing import List
from sqlalchemy import ForeignKey, String, Date, Numeric, Identity, BigInteger
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship

from mesonet_utils import Config
from pathlib import Path
import psycopg
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

CONFIG = Config.load(Config.file)
token: str = CONFIG.airtable_token
schema: Path = CONFIG.directory / "at_schema.json"

if CONFIG.env_file.exists():
    load_dotenv(CONFIG.env_file)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Stations(Base):
    __tablename__ = 'stations'
    __table_args__ = (
        UniqueConstraint("station"),
        {'schema': "data"},
    )    

    station: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    status: Mapped[str] = mapped_column(String, CheckConstraint("status IN ('pending', 'active', 'decommissioned', 'inactive')"))
    date_installed: Mapped[date]
    latitude: Mapped[float]
    longitude: Mapped[float]
    elevation: Mapped[float]
    sensors: Mapped[List["Sensors"]] = relationship("Sensors", secondary="station_sensors", back_populates="stations")


class Sensors(Base):
    __tablename__ = 'sensors'
    __table_args__ = (
        UniqueConstraint("model", "serial_number"),
        {'schema': "data"},
    )

    model: Mapped[str] = mapped_column(primary_key=True)
    serial_number: Mapped[str] = mapped_column(primary_key=True)
    date_start: Mapped[date] = mapped_column(primary_key=True)
    date_end: Mapped[date]
    station: Mapped[str] = mapped_column(ForeignKey("stations.station"))
    stations: Mapped[List["Stations"]] = relationship("Stations", secondary="station_sensors", back_populates="sensors")
    elements: Mapped[List["Elements"]] = relationship("Elements", secondary="sensor_elements", back_populates="sensors")


class StationSensors(Base):
    __tablename__ = 'station_sensors'
    __table_args__ = {'schema': "data"}

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    station: Mapped[str] = mapped_column(String, ForeignKey("stations.station"))
    model: Mapped[str] = mapped_column(String, ForeignKey("sensors.model"))
    serial_number: Mapped[str] = mapped_column(String, ForeignKey("sensors.serial_number"))
    date_start: Mapped[date] = mapped_column(Date, ForeignKey("sensors.date_start"))

class Elements(Base):
    __tablename__ = 'elements'
    __table_args__ = (
        UniqueConstraint("element"),
        {'schema': "data"},
    )

    element: Mapped[str] = mapped_column(primary_key=True)
    public: Mapped[bool]
    description: Mapped[str]
    description_short: Mapped[str]
    si_units: Mapped[str]
    us_units: Mapped[str]
    sensors: Mapped[List["Sensors"]] = relationship("Sensors", secondary="sensor_elements", back_populates="elements")


class SensorElements(Base):
    __tablename__ = 'sensor_elements'
    __table_args__ = (
        {'schema': "data"}
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    element: Mapped[str] = relationship(ForeignKey("elements.element"))
    sensor: Mapped[str] = relationship(ForeignKey("sensors.model"))






