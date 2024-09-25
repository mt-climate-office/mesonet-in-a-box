from mbx_inventory.schemas import BaseSchema
from pathlib import Path

base_schema = BaseSchema.load(Path("/home/cbrust/.config/mbx/p6qk9g7kprqubv6.json"))


def fix_stations_table(base_schema):
    stations = base_schema["Stations"]
