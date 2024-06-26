import httpx
import asyncio
from config import Config
from pathlib import Path

from airtable import (
    get_stations,
    get_elements,
)  # , get_deployments, get_model_elements, get_elements

API_URL = "http://127.0.0.1:8000"


async def post_stations(token: str, schema: Path) -> None:
    stations = await get_stations(token=token, schema=schema, as_json=True)
    async with httpx.AsyncClient() as client:
        for station in stations:
            station["deployments"] = []
            station["request_schemas"] = []
            station["response_schemas"] = []
            response = await client.post(f"{API_URL}/stations", json=station)
            print(response.text)


async def post_elements(token: str, schema: Path) -> None:
    elements = await get_elements(token=token, schema=schema, as_json=True)
    async with httpx.AsyncClient() as client:
        for element in elements:
            element["models"] = []
            response = await client.post(f"{API_URL}/elements", json=element)
            print(response.text)


if __name__ == "__main__":
    CONFIG = Config.load(Config.file)
    schema: Path = CONFIG.directory / "at_schema.json"
    token = CONFIG.airtable_token

    # asyncio.run(post_elements(token, schema))
    asyncio.run(post_stations(token, schema))
