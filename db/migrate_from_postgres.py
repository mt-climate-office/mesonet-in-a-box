from pymongo import MongoClient
import datetime as dt
import httpx



CONNECTION_STRING = "mongodb://localhost:27017/"

def make_stations_document(index_name: str = "station") -> None:
    request = httpx.get("https://mesonet.climate.umt.edu/api/stations?type=json")
    if not request.status_code == 200:
        raise httpx.RequestError("Bad Request!")
    stations = request.json()

    db = MongoClient(CONNECTION_STRING)
    db = db["mesonet"]
    collection = db["stations"]
    collection.create_index([(index_name, 1)], unique=True)

    for station in stations:
        station['date_installed'] = dt.datetime.strptime(station['date_installed'], "%Y-%m-%d")
    
    collection.insert_many(stations)


def make_elements_document(index_name: str = "element") -> None:
    request = httpx.get("https://mesonet.climate.umt.edu/api/elements?type=json")
    if not request.status_code == 200:
        raise httpx.RequestError("Bad Request!")
    elements = request.json()

    for element in elements:
        
