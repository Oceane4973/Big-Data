import os
import requests
import datetime

from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
from dotenv import load_dotenv

# Load env variables
load_dotenv()


# Config
SNCF_TOKEN = os.getenv("SNCF_API_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
STOP_AREA_MARSEILLE="stop_area:SNCF:87751008"

def fetch_marseille_arrivals():
    auth = HTTPBasicAuth(SNCF_TOKEN, "")

    params = {
        "count": 1000
    }

    response = requests.get(
        f"{BASE_URL}/stop_areas/{STOP_AREA_MARSEILLE}/arrivals",
        auth=auth,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def save_to_mongo(data):
    client = MongoClient(MONGO_URI)

    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    stop_areas = data.get("stop_areas", [])

    if not stop_areas:
        print("WARNING: No data")
        return

    now = datetime.datetime.utcnow()
    docs = []

    for area in stop_areas:
        area["_ingestion_date"] = now
        area["_source"] = "sncf_api"

        docs.append(area)

    # Insertion bulk
    result = collection.insert_many(docs)
    print(f"{len(result.inserted_ids)} documents insérés")

    client.close()


def main():
    try:
        data = fetch_marseille_arrivals()
        save_to_mongo(data)

        print("SUCCES: Data saved")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()