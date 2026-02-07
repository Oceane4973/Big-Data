import os
import requests
import datetime
import pytz

from requests.auth import HTTPBasicAuth
from pymongo import MongoClient, UpdateOne
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Get variables from env
SNCF_TOKEN = os.getenv("SNCF_API_TOKEN")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CONTAINER_NAME = os.getenv("MONGO_CONTAINER_NAME")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CONTAINER_NAME}:27017/?authSource=admin"
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

BASE_URL = "https://api.sncf.com/v1/coverage/sncf"
STOP_AREA_MARSEILLE="stop_area:SNCF:87751008"

def fetch_marseille_arrivals():
    auth = HTTPBasicAuth(SNCF_TOKEN, "")

    params = {
        "count": 100
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

    arrivals = data.get("arrivals", [])

    if not arrivals:
        print("WARNING: No data arrivals")
        return

    now = datetime.datetime.now(pytz.UTC)
    operations = []

    for area in arrivals:
        # Search vehicule journey ID
        vj_link = next(
            (l for l in area.get("links", []) if l.get("type") == "vehicle_journey"),
            None
        )

        if not vj_link:
            continue

        area["_id"] = vj_link["id"]
        area["_ingestion_date"] = now
        area["_preprocessed"] = False
        area["_source"] = "sncf_api"

        operations.append(
            UpdateOne(
                {"_id": vj_link["id"]},
                {"$setOnInsert": area},
                upsert=True
            )
        )

    if operations:
        result = collection.bulk_write(operations, ordered=False)
        print(
            f"Inserted: {result.upserted_count}, "
            f"Matched existing: {result.matched_count}"
        )

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