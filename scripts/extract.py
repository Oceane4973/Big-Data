import os
import requests
import datetime

from requests.auth import HTTPBasicAuth
from pymongo import MongoClient
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

def fetch_marseille_disruptions():
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

    disruptions = data.get("disruptions", [])

    if not disruptions:
        print("WARNING: No data")
        return

    now = datetime.datetime.now(datetime.UTC)
    docs = []

    for area in disruptions:
        area["_ingestion_date"] = now
        area["_source"] = "sncf_api"

        docs.append(area)

    # Insertion bulk
    result = collection.insert_many(docs)
    print(f"{len(result.inserted_ids)} documents insérés")

    client.close()


def main():
    try:
        data = fetch_marseille_disruptions()
        save_to_mongo(data)

        print("SUCCES: Data saved")

    except Exception as e:
        print(f"ERROR: {e}")
        raise


if __name__ == "__main__":
    main()