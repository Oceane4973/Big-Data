import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, lit, when

# Récupération des variables d'environnement
MONGO_DATALAKE_HOST = os.getenv("MONGO_CONTAINER_NAME")
MONGO_DATALAKE_USER = os.getenv("MONGO_USER")
MONGO_DATALAKE_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_DATALAKE_DB = os.getenv("MONGO_DB")
MONGO_DATALAKE_COLLECTION = os.getenv("MONGO_COLLECTION")
POSTRGES_ORGANIZED_HOST = os.getenv("POSTGRES_CONTAINER_NAME")
POSTRGES_ORGANIZED_USER = os.getenv("POSTGRES_USER")
POSTRGES_ORGANIZED_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTRGES_ORGANIZED_DB = os.getenv("POSTGRES_DB")

# Création de la session Spark avec support MongoDB, Postgres
spark = SparkSession.builder \
    .appName("MongoDB_to_Postgres") \
    .config("spark.mongodb.read.connection.uri", f"mongodb://{MONGO_DATALAKE_USER}:{MONGO_DATALAKE_PASSWORD}@{MONGO_DATALAKE_HOST}:27017/{MONGO_DATALAKE_DB}.{MONGO_DATALAKE_COLLECTION}?authSource=admin") \
    .config("spark.mongodb.write.connection.uri", f"mongodb://{MONGO_DATALAKE_USER}:{MONGO_DATALAKE_PASSWORD}@{MONGO_DATALAKE_HOST}:27017/{MONGO_DATALAKE_DB}.{MONGO_DATALAKE_COLLECTION}?authSource=admin") \
    .getOrCreate()

# Logo Mongo data
arrivals_raw = spark.read.format("mongodb") \
    .option("aggregation.pipeline", '[{"$match": {"_preprocessed": false}}]') \
    .load()

# Verify if at least one raw exists
if arrivals_raw.rdd.isEmpty():
    print("INFO: Aucun enregistrement à traiter (_preprocessed=false). Fin du script.")
    sys.exit(0) 

# Select formatted data for Postgres
arrivals_final = arrivals_raw.select(
    col("_id").alias("train_id"),
    to_timestamp(col("stop_date_time").getField("departure_date_time"), "yyyyMMdd'T'HHmmss").alias("departure_actual"),
    to_timestamp(col("stop_date_time").getField("base_departure_date_time"), "yyyyMMdd'T'HHmmss").alias("departure_scheduled"),
    to_timestamp(col("stop_date_time").getField("arrival_date_time"), "yyyyMMdd'T'HHmmss").alias("arrival_actual"),
    to_timestamp(col("stop_date_time").getField("base_arrival_date_time"), "yyyyMMdd'T'HHmmss").alias("arrival_scheduled"),
    col("stop_point").getField("name").alias("stop_name"),
    col("stop_point").getField("physical_modes").getItem(0).getField("name").alias("train_type"),
    col("display_informations").getField("name").alias("train_name"),
)
# Add column to know if arrival is late
arrivals_final = arrivals_final.withColumn(
    "arrival_is_late",
    when(col("arrival_actual") > col("arrival_scheduled"), lit(True)).otherwise(lit(False))
)
# Add column to know if departure is late
arrivals_final = arrivals_final.withColumn(
    "departure_is_late",
    when(col("departure_actual") > col("departure_scheduled"), lit(True)).otherwise(lit(False))
)

# Insert data into Postgres
arrivals_final.write \
    .format("jdbc") \
    .option("url", f"jdbc:postgresql://{POSTRGES_ORGANIZED_HOST}:5432/{POSTRGES_ORGANIZED_DB}") \
    .option("dbtable", "marseille_arrivals") \
    .option("user", POSTRGES_ORGANIZED_USER) \
    .option("password", POSTRGES_ORGANIZED_PASSWORD) \
    .option("driver", "org.postgresql.Driver") \
    .mode("append") \
    .save()

# Update field _preprocessed in Mongo
arrivals_raw.withColumn("_preprocessed", lit(True)) \
    .write \
    .format("mongodb") \
    .option("replaceDocument", "true") \
    .mode("append") \
    .save()