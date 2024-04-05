import httpx
import polars as pl
from os import getenv
from pathlib import Path
import json
from typing import Any, Optional

from dataclasses import dataclass


from dotenv import load_dotenv

load_dotenv("../../.env")


@dataclass
class Table:
    name: str
    short_name: str
    id: str

    def __eq__(self, other: str) -> bool:
        return self.name == other or self.short_name == other or self.id == other


def search_tables_for_match(tables: list[Table], search_val: str) -> Table:
    for table in tables:
        if table == search_val:
            return table.id

    raise ValueError(
        f"The specified table ({search_val}) could not be found in your schema file."
    )


def load_airtable_schema(schema: Path = Path("../at_schema.json")) -> dict[str, Any]:
    schema = json.load(schema.open())
    schema["tables"] = [Table(**x) for x in schema["tables"]]
    return schema


def _get_records(
    url: str,
    headers: dict[str, str],
    params: dict[str, Any],
    cur_records: Optional[list[dict[str, Any]]] = None,
) -> tuple[list[dict[str, Any]], str]:
    if cur_records is None:
        cur_records = []

    response = httpx.get(url=url, headers=headers, params=params)

    data = response.json()
    cur_records += data["records"]

    return cur_records, data.get("offset", None)


def get_airtable_records(
    schema: dict[str, Any],
    table: str,
    fields: Optional[list[str]] = None,
    formula: str = None,
):
    table = search_tables_for_match(schema["tables"], table)
    url = f"{schema['api_url']}{schema['base_id']}/{table}"
    headers = {"Authorization": f"Bearer {getenv('AIRTABLE_API_KEY')}"}

    params = {}
    if fields:
        params["fields[]"] = fields

    if formula:
        params["filterByFormula"] = formula

    data, offset = _get_records(url, headers, params, None)
    while offset:
        params = {"offset": offset}
        data, offset = _get_records(url, headers, {"offset": offset}, data)

    out = []
    for record in data:
        record["fields"]["record"] = record["id"]
        record_fields = record["fields"]
        record_fields = {
            k: v[0] if isinstance(v, list) else v for k, v in record_fields.items()
        }
        out.append(record["fields"])

    return pl.DataFrame(out)
