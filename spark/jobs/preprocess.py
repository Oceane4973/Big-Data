from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("SNCF-Processing") \
    .getOrCreate()


# Exemple test
df = spark.createDataFrame([
    ("Paris", 5),
    ("Dakar", 12)
], ["station", "delay"])


df.show()


spark.stop()