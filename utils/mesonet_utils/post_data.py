import httpx
import asyncio
from config import Config
from pathlib import Path
from typing import Any

from airtable import get_stations  # , get_deployments, get_model_elements, get_elements

CONFIG = Config.load(Config.file)
schema: Path = CONFIG.directory / "at_schema.json"
token = CONFIG.airtable_token


async def post_stations(token: str, schema: Path) -> dict[str, Any]:
    stations = await get_stations(token=token, schema=schema, as_json=True)
    async with httpx.AsyncClient() as client:
        for station in stations:
            print(station)
            r = await client.post("http://127.0.0.1:8000/stations", json=station)
            print(r.text)
            print(r)
    return stations


asyncio.run(post_stations(token, schema))
