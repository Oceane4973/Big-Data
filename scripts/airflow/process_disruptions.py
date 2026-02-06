import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_CONTAINER_NAME"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    port=os.getenv("POSTGRES_CONTAINER_PORT")
)

cur = conn.cursor()

SNCF_TOKEN = os.getenv("SNCF_API_TOKEN")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_CONTAINER_NAME = os.getenv("MONGO_CONTAINER_NAME")

MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_CONTAINER_NAME}:27017/?authSource=admin"
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

def fetch_from_mongo():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    documents = list(collection.find({}))

    client.close()
    return documents

def save_to_postgres(data):
    perturbations = []
    endroits = []
    liaisons = []

    for doc in data:
        id_perturbation = doc.get("id")
        if not id_perturbation:
            continue
        messages = doc.get("messages", [])
        origine = messages[0].get("text") if messages else ""
        
        perturbations.append((
            id_perturbation,
            origine
        ))

        impacted_objects = doc.get("impacted_objects", [])
        points_arret = impacted_objects[0].get("impacted_stops", []) if impacted_objects else []
        for point_arret in points_arret:
            stop_point = point_arret.get("stop_point", {})
            coord = stop_point.get("coord", {})

            id_endroit = stop_point.get("id")
            nom = stop_point.get("name")
            longitude = coord.get("lon")
            latitude = coord.get("lat")
            
            endroits.append((
                id_endroit,
                nom,
                longitude,
                latitude,
            ))

            base_arrival_time = point_arret.get("base_arrival_time")
            base_departure_time = point_arret.get("base_departure_time")
            amended_arrival_time = point_arret.get("amended_arrival_time")
            amended_departure_time = point_arret.get("amended_departure_time")

            if amended_departure_time is None:
                print(id_perturbation, point_arret)

            liaisons.append((
                id_perturbation,
                id_endroit,
                base_arrival_time,
                base_departure_time,
                amended_arrival_time,
                amended_departure_time,
            ))            


    execute_batch(
        cur,
        """
        INSERT INTO Perturbations (id_perturbation, origine)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING
        """,
        perturbations,
        page_size=100
    )
    execute_batch(
        cur,
        """
        INSERT INTO Endroits (id_endroit, nom, longitude, latitude)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        endroits,
        page_size=100
    )
    execute_batch(
        cur,
        """
        INSERT INTO points_arrets (id_perturbation, id_endroit, base_arrival_time, base_departure_time, amended_arrival_time, amended_departure_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        liaisons,
        page_size=100
    )

    # print(perturbations)
    # print(endroits)
    # print(liaisons)

    conn.commit()


def main():
    try:
        data = fetch_from_mongo()
        save_to_postgres(data)

        print("SUCCES: Data saved")

    except Exception as e:
        print(f"ERROR: {e}")
        raise

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()