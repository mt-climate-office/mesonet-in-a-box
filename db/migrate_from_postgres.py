from pymongo import MongoClient
import datetime as dt
import httpx
from dotenv import load_dotenv
from pathlib import Path
from os import getenv
from decimal import Decimal

from sqlalchemy import create_engine, URL, MetaData
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

load_dotenv(
    Path("~/git/mesonet-in-a-box/.env").expanduser()
)

CONNECTION_STRING = f"mongodb://{getenv('MONGO_INITDB_ROOT_USERNAME')}:{getenv('MONGO_INITDB_ROOT_PASSWORD')}@localhost:27017/?authSource=admin"

def connect_to_db():
    PG_CONN = URL.create(
        "postgresql",
        username=getenv("PGUSER"),
        password=getenv("PGPASS"),  # plain (unescaped) text
        host=getenv("PGHOST"),
        database=getenv("PGDB"),
    )
    m = MetaData(schema="data")
    Base = automap_base(metadata=m)
    engine = create_engine(PG_CONN)
    Base.prepare(engine, reflect=True)

    return Base, engine


def query_to_dict(result):
    out = []
    for row in result:
        out.append({column.name: getattr(row, column.name) for column in row.__table__.columns})
    return out


# TODO: Just read this from airtable!!!
def get_stations():
    base, engine = connect_to_db()

    with Session(engine) as session:
        q = session.query(base.classes.stations)
        dat = query_to_dict(q.all())
    return dat

def get_elements():
    base, engine = connect_to_db()

    with Session(engine) as session:
        q = session.query(base.classes.elements)
        dat = query_to_dict(q.all())
    return dat

def make_stations_document(index_name: str = "station") -> None:
    client = MongoClient(CONNECTION_STRING)
    db = client["mesonet"]
    collection = db["stations"]
    collection.create_index([(index_name, 1)], unique=True)

    stations = get_stations()
    stations_out = []
    for station in stations:
        station_out = {}
        if station.get('date_installed'):
            station['date_installed'] = dt.datetime.combine(station['date_installed'], dt.datetime.min.time())
        for k, v in station.items():
            if isinstance(v, Decimal):
                v = float(v)
            station_out[k] = v
        stations_out.append(station_out)
    collection.insert_many(stations_out)


# def make_elements_document(index_name: str = "element") -> None:
#     request = httpx.get("https://mesonet.climate.umt.edu/api/elements?type=json")
#     if not request.status_code == 200:
#         raise httpx.RequestError("Bad Request!")
#     elements = request.json()

#     for element in elements:
        
