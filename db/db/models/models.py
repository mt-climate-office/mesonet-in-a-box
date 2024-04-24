from __future__ import annotations
from datetime import date, datetime
from typing import List, Any
from sqlalchemy import ForeignKey, String, Identity, Date, Numeric
from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.orm import relationship
from typing import Optional
from sqlalchemy.dialects.postgresql import JSONB


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {dict[str, Any]: JSONB}


class Elements(Base):
    __tablename__ = "elements"
    __table_args__ = ({"schema": "network"},)

    element: Mapped[str] = mapped_column(String, primary_key=True)
    public: Mapped[bool]
    description: Mapped[str]
    description_short: Mapped[str]
    si_units: Mapped[str] = mapped_column(String, nullable=True)
    us_units: Mapped[str] = mapped_column(String, nullable=True)
    attributes = mapped_column(JSONB, nullable=True)
    models: Mapped[List["ComponentModels"]] = relationship(
        "ComponentModels",
        secondary="network.component_elements",
        back_populates="elements",
        uselist=True,
    )


class ComponentModels(Base):
    __tablename__ = "component_models"
    __table_args__ = {"schema": "network"}

    model: Mapped[str] = mapped_column(primary_key=True)
    manufacturer: Mapped[str]
    type: Mapped[str]
    elements: Mapped[List["Elements"]] = relationship(
        "Elements", secondary="network.component_elements", back_populates="models"
    )


class ComponentElements(Base):
    __tablename__ = "component_elements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["model"],
            [
                "network.component_models.model",
            ],
        ),
        {"schema": "network"},
    )

    model: Mapped[str] = mapped_column(
        String, ForeignKey("network.component_models.model"), primary_key=True
    )
    element: Mapped[str] = mapped_column(
        String, ForeignKey("network.elements.element"), primary_key=True
    )
    qc_values = mapped_column(JSONB)


class Stations(Base):
    __tablename__ = "stations"
    __table_args__ = (
        UniqueConstraint("station"),
        {"schema": "network"},
    )

    station: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(
        String,
        CheckConstraint(
            "status IN ('pending', 'active', 'decommissioned', 'inactive')"
        ),
        nullable=False,
    )
    date_installed: Mapped[date | None] = mapped_column(Date, nullable=True)
    latitude: Mapped[float]
    longitude: Mapped[float]
    elevation: Mapped[float]
    deployments: Mapped[Optional[List["Deployments"]]] = relationship(
        "Deployments", back_populates="station_relationship", uselist=True
    )


class Inventory(Base):
    __tablename__ = "inventory"
    __table_args__ = (UniqueConstraint("model", "serial_number"), {"schema": "network"})

    model: Mapped[str] = mapped_column(
        ForeignKey("network.component_models.model"), primary_key=True
    )
    serial_number: Mapped[str] = mapped_column(primary_key=True)
    attributes = mapped_column(JSONB, nullable=True)
    deployments: Mapped[List["Deployments"]] = relationship(
        "Deployments", back_populates="inventory"
    )


class Deployments(Base):
    __tablename__ = "deployments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["model", "serial_number"],
            ["network.inventory.model", "network.inventory.serial_number"],
        ),
        UniqueConstraint("station", "model", "serial_number", "date_assigned"),
        UniqueConstraint("id"),
        {"schema": "network"},
    )

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    station: Mapped[str] = mapped_column(
        ForeignKey("network.stations.station"),
        index=True,
        primary_key=True,
    )
    model: Mapped[str] = mapped_column(index=True, nullable=False, primary_key=True)
    serial_number: Mapped[str] = mapped_column(nullable=False, primary_key=True)
    date_assigned: Mapped[date] = mapped_column(nullable=False, primary_key=True)
    date_start: Mapped[date] = mapped_column(nullable=True)
    date_end: Mapped[date] = mapped_column(Date, nullable=True)
    inventory: Mapped["Inventory"] = relationship(
        "Inventory", back_populates="deployments"
    )
    observations: Mapped[List["Observations"]] = relationship(
        "Observations", back_populates="deployment_relationship"
    )
    station_relationship: Mapped["Stations"] = relationship(
        "Stations", back_populates="deployments"
    )


class Raw(Base):
    __tablename__ = "raw"
    __table_args__ = {"schema": "data"}

    station: Mapped[str] = mapped_column(
        ForeignKey("network.stations.station"), primary_key=True
    )

    datetime: Mapped[datetime]
    created_at: Mapped[datetime]  # type: ignore
    data = mapped_column(JSONB)


class Observations(Base):
    __tablename__ = "observations"
    __table_args__ = {"schema": "data"}

    station: Mapped[str] = mapped_column(
        ForeignKey("network.stations.station"), primary_key=True
    )
    element: Mapped[str] = mapped_column(
        ForeignKey("network.elements.element"), primary_key=True
    )
    deployment: Mapped[int] = mapped_column(
        ForeignKey("network.deployments.id"), primary_key=True, index=True
    )
    datetime: Mapped[datetime] = mapped_column(primary_key=True, index=True)
    value: Mapped[float]
    qc_flags: Mapped[int] = mapped_column(Numeric, nullable=True)
    deployment_relationship: Mapped["Deployments"] = relationship(
        "Deployments", back_populates="observations"
    )
