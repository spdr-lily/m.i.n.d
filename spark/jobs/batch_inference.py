from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, udf, desc, lit, row_number
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from pyspark.sql.window import Window

from spark.config import DB_URL, JDBC_URL, DB_PROPERTIES, SPARK_MASTER


def create_session(app_name: str = "mind-batch-inference") -> SparkSession:
    return (
        SparkSession.builder
        .appName(app_name)
        .master(SPARK_MASTER)
        .config("spark.jars", "postgresql-42.7.1.jar")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def load_consultations(spark: SparkSession) -> DataFrame:
    return (
        spark.read.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "clinical.clinical_consultation")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .load()
        .filter(col("inference_status") == "pending")
    )


def load_symptoms(spark: SparkSession) -> DataFrame:
    return (
        spark.read.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "clinical.symptom_observation")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .load()
    )


def load_disorders(spark: SparkSession) -> DataFrame:
    return (
        spark.read.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "diagnostic.disorders")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .load()
    )


def write_inferences(df: DataFrame):
    (
        df.write
        .format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", "diagnostic.diagnostic_inference")
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .mode("append")
        .save()
    )


def run_batch_inference():
    spark = create_session()
    try:
        consultations = load_consultations(spark)
        symptoms = load_symptoms(spark)
        disorders = load_disorders(spark)

        total_pending = consultations.count()
        if total_pending == 0:
            print("No pending consultations")
            return {"processed": 0}

        symptom_counts = (
            symptoms.groupBy("consultation_uuid")
            .agg({"symptom_id": "count"})
            .withColumnRenamed("count(symptom_id)", "symptom_count")
        )

        consultations_with_symptoms = consultations.join(
            symptom_counts, "consultation_uuid", "left"
        ).fillna(0)

        disorder_count = disorders.count()
        inferences_df = (
            consultations_with_symptoms.crossJoin(disorders)
            .select(
                col("consultation_uuid"),
                col("disorder_id"),
                lit(0.5).alias("inference_probability"),
            )
        )

        write_inferences(inferences_df)

        print(f"Processed {total_pending} consultations")
        return {"processed": total_pending}
    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_batch_inference()
    print(f"Result: {result}")
