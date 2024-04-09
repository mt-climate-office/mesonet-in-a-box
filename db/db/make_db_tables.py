from airtable import get_airtable_records, load_airtable_schema
import polars as pl
from mesonet_utils import Config
from pathlib import Path

CONFIG = Config.load(Config.file)


def get_stations(
    token: str = CONFIG.airtable_token,
    schema: Path = CONFIG.directory / "at_schema.json",
) -> pl.DataFrame:
    stations = get_airtable_records(
        schema=load_airtable_schema(schema),
        token=token,
        table="stations",
        fields=[
            "name",
            "station",
            "status",
            "date_installed",
            "nwsli_id",
            "sub_network",
            "latitude",
            "longitude",
            "report_mco",
            "elevation",
            "ace_grid",
        ],
    )

    return stations
