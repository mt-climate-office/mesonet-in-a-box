from __future__ import annotations

import httpx
import polars as pl
from pathlib import Path
import json
from typing import Any, Optional

from dataclasses import dataclass


@dataclass
class Table:
    name: str
    short_name: str
    id: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Table):
            return (
                self.name == other.name
                or self.short_name == other.name
                or self.id == other.name
            )

        raise NotImplementedError(
            f"Table equal comparison not implemented for type: {type(other)}"
        )


def search_tables_for_match(tables: list[Table], search_val: str) -> str:
    for table in tables:
        if table == Table(search_val, search_val, search_val):
            return table.id

    raise ValueError(
        f"The specified table ({search_val}) could not be found in your schema file."
    )


def load_airtable_schema(schema: Path = Path("../at_schema.json")) -> dict[str, Any]:
    schema_dict = json.load(schema.open())
    schema_dict["tables"] = [Table(**x) for x in schema_dict["tables"]]
    return schema_dict


async def _get_records(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
    cur_records: Optional[list[dict[str, Any]]] = None,
) -> tuple[list[dict[str, Any]], str]:
    if cur_records is None:
        cur_records = []

    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers, params=params)

    data = response.json()
    cur_records += data["records"]

    return cur_records, data.get("offset", None)


async def get_airtable_records(
    schema: dict[str, Any],
    token: str,
    table: str,
    fields: Optional[list[str]] = None,
    formula: Optional[str] = None,
    with_record: bool = False,
) -> pl.DataFrame:
    table = search_tables_for_match(schema["tables"], table)
    url = f"{schema['api_url']}{schema['base_id']}/{table}"
    headers = {"Authorization": f"Bearer {token}"}

    params: dict[str, Any] = {}
    if fields:
        params["fields[]"] = fields

    if formula:
        params["filterByFormula"] = formula

    data, offset = await _get_records(url, headers, params, None)
    while offset:
        params = {"offset": offset}
        data, offset = await _get_records(url, headers, {"offset": offset}, data)

    out = []
    for record in data:
        if with_record:
            record["fields"]["record"] = record["id"]

        out.append(record["fields"])

    return pl.DataFrame(out)


def unlist_len1_list_columns(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        col.list.first()
        for col in df
        if col.dtype == pl.List and col.list.len().max() == 1
    )


def additional_columns_to_struct(
    df: pl.DataFrame, req_columns: list[str], additional_fields: list[str] | None = None
) -> pl.DataFrame:
    additional = list(set(df.columns) - set(req_columns))
    if additional_fields is not None:
        additional = [x for x in additional if x in additional_fields]
    df = df.with_columns(extra_data=pl.struct(additional))[req_columns + ["extra_data"]]

    return df


REQ_STATION_FIELDS = [
    "station",
    "name",
    "status",
    "date_installed",
    "latitude",
    "longitude",
    "elevation",
]


async def get_stations(
    token: str,
    schema: Path,
    additional_fields: list[str] | None = None,
    as_json: bool = False,
) -> pl.DataFrame | list[dict[str, Any]]:
    if additional_fields is not None:
        fields = REQ_STATION_FIELDS + additional_fields
    else:
        fields = None
    stations = await get_airtable_records(
        schema=load_airtable_schema(schema),
        token=token,
        table="stations",
        fields=fields,
    )
    stations = unlist_len1_list_columns(stations)
    stations = additional_columns_to_struct(
        stations, REQ_STATION_FIELDS, additional_fields
    )

    assert all(
        x in stations.columns for x in REQ_STATION_FIELDS
    ), f"All the following fields must be present in your stations table. Please check that they are present in AirTable: {REQ_STATION_FIELDS}"
    if as_json:
        return stations.to_dicts()
    return stations


# TODO: Implement adjustment to return so that all fields not in db get put into the attributes dict
async def get_elements(
    token: str,
    schema: Path,
    as_json: bool = False,
) -> pl.DataFrame | list[dict[str, Any]]:
    elements = await get_airtable_records(
        schema=load_airtable_schema(schema),
        token=token,
        table="elements",
        fields=[
            "element",
            "public",
            "description",
            "description_short",
            "zentra_name",
            "ace_name",
            "base_units",
            "us_units",
            "usace_units",
        ],
    )

    elements = unlist_len1_list_columns(elements)

    elements = elements.with_columns(
        pl.col("element").str.replace("_{elevation_cm}", "", literal=True),
        pl.col("description_short").str.replace("@ {elevation_cm}", "", literal=True),
        pl.col("description").str.replace("at {elevation_cm}", "", literal=True),
    )
    if as_json:
        return elements.to_dicts()
    return elements


async def get_deployments(
    token: str,
    schema: Path,
    as_json: bool = False,
) -> pl.DataFrame | list[dict[str, Any]]:
    deployments = await get_airtable_records(
        schema=load_airtable_schema(schema),
        token=token,
        table="deployments",
        fields=[
            "station_key",
            "serial_number",
            "model",
            "port",
            "sdi12_address",
            "elevation_cm",
            "date_start",
            "date_end",
        ],
    )

    deployments = unlist_len1_list_columns(deployments)
    deployments = deployments.with_columns(
        pl.col("date_start").cast(pl.Date), pl.col("date_end").cast(pl.Date)
    )
    if as_json:
        return deployments.to_dicts()
    return deployments


async def get_model_elements(
    token: str,
    schema: Path,
    as_json: bool = False,
) -> pl.DataFrame | list[dict[str, Any]]:
    model_elements = await get_airtable_records(
        schema=load_airtable_schema(schema),
        token=token,
        table="model_elements",
        fields=[
            "model",
            "element",
            "range_min",
            "range_max",
            "step_size",
            "persistence_delta",
            "spatial_sd",
            "flag_min",
            "flag_max",
            "shared_sensor",
            "like_element",
        ],
    )

    model_elements = unlist_len1_list_columns(model_elements)
    model_elements = model_elements.with_columns(
        pl.col("element").str.replace("_{elevation_cm}", "", literal=True),
    )
    if as_json:
        return model_elements.to_dicts()
    return model_elements
