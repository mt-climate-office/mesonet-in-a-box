import httpx
import asyncio
from config import Config
from pathlib import Path

from airtable import (
    get_stations,
    get_elements,
)  # , get_deployments, get_model_elements, get_elements


async def post_stations(token: str, schema: Path) -> None:
    stations = await get_stations(token=token, schema=schema, as_json=True)
    async with httpx.AsyncClient() as client:
        for station in stations:
            # station["deployments"] = []
            r = await client.post("http://127.0.0.1:8000/stations", json=station)
            print(r.text)


async def post_elements(token: str, schema: Path) -> None:
    elements = await get_elements(token=token, schema=schema, as_json=True)
    async with httpx.AsyncClient() as client:
        for element in elements:
            print(element)
            r = await client.post("http://127.0.0.1:8000/elements", json=element)
            print(r.text)
            break


if __name__ == "__main__":
    CONFIG = Config.load(Config.file)
    schema: Path = CONFIG.directory / "at_schema.json"
    token = CONFIG.airtable_token

    asyncio.run(post_elements(token, schema))
    # asyncio.run(post_stations(token, schema))
