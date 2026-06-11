from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, lit, when, current_timestamp, expr
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType, DateType,
)

from spark.config import JDBC_URL, DB_PROPERTIES, SPARK_MASTER


BULK_INSERT_BATCH_SIZE = 500


def create_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("mind-data-import")
        .master(SPARK_MASTER)
        .config("spark.jars", "postgresql-42.7.1.jar")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )


CSV_SYMPTOM_SCHEMA = StructType([
    StructField("symptom_name", StringType(), True),
    StructField("cid_code", StringType(), True),
    StructField("symptom_description", StringType(), True),
])


CSV_PATIENT_SCHEMA = StructType([
    StructField("full_name", StringType(), True),
    StructField("birth_date", DateType(), True),
    StructField("sex", StringType(), True),
])


def import_symptoms_from_csv(spark: SparkSession, csv_path: str) -> int:
    df = (
        spark.read.option("header", True)
        .schema(CSV_SYMPTOM_SCHEMA)
        .csv(csv_path)
        .withColumn("symptom_id", expr("uuid()"))
        .withColumn("created_at", current_timestamp())
        .select("symptom_id", "symptom_name", "cid_code", "symptom_description", "created_at")
    )

    count = df.count()
    (
        df.write.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "diagnostic.symptoms")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .mode("append")
        .option("batchsize", BULK_INSERT_BATCH_SIZE)
        .save()
    )
    return count


def import_patients_from_csv(spark: SparkSession, csv_path: str) -> dict:
    df = (
        spark.read.option("header", True)
        .schema(CSV_PATIENT_SCHEMA)
        .csv(csv_path)
    )

    identities = df.select(
        expr("uuid()").alias("patient_uuid"),
        col("full_name"),
        lit("imported").alias("cpf_hash"),
        lit("imported").alias("email_hash"),
        current_timestamp().alias("created_at"),
    )

    profiles = df.select(
        col("patient_uuid"),
        col("birth_date"),
        when(col("sex") == "M", 1).otherwise(2).alias("sex_type_id"),
        lit(None).cast("int").alias("gender_identity_id"),
        current_timestamp().alias("created_at"),
    )

    total = df.count()

    (
        identities.write.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "security.patient_identity")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .mode("append")
        .option("batchsize", BULK_INSERT_BATCH_SIZE)
        .save()
    )

    (
        profiles.write.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "clinical.patient_profile")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .mode("append")
        .option("batchsize", BULK_INSERT_BATCH_SIZE)
        .save()
    )

    return {"imported_patients": total}


if __name__ == "__main__":
    spark = create_session()
    try:
        result = import_patients_from_csv(spark, "data/patients.csv")
        print(f"Import result: {result}")
    finally:
        spark.stop()
