import airtable
from mesonet_utils import Config
import pytest


pytest_plugins = ("pytest_asyncio",)
CONFIG = Config.load(Config.file)


@pytest.mark.asyncio
async def test_get_stations():
    await airtable.get_stations(
        schema=CONFIG.directory / "at_schema.json",
        token=CONFIG.airtable_token,
        additional_fields=[
            "nwsli_id",
            "sub_network",
            "report_mco",
            "report_mesowest",
            "ace_grid",
        ],
    )
    assert True
