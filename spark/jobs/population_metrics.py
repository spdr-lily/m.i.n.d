from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, count, avg, stddev, when, year, datediff, current_date,
    round, desc, lit,
)

from spark.config import JDBC_URL, DB_PROPERTIES, SPARK_MASTER


def create_session() -> SparkSession:
    return (
        SparkSession.builder
        .appName("mind-population-metrics")
        .master(SPARK_MASTER)
        .config("spark.jars", "postgresql-42.7.1.jar")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )


def load_table(spark: SparkSession, table: str) -> DataFrame:
    return (
        spark.read.format("jdbc")
        .option("url", JDBC_URL)
        .option("dbtable", table)
        .option("user", DB_PROPERTIES["user"])
        .option("password", DB_PROPERTIES["password"])
        .option("driver", DB_PROPERTIES["driver"])
        .load()
    )


def age_distribution(profiles: DataFrame) -> DataFrame:
    return (
        profiles.withColumn(
            "age_group",
            when(col("birth_date").isNotNull(),
                 when(year(current_date()) - year(col("birth_date")) <= 18, "0-18")
                 .when(year(current_date()) - year(col("birth_date")) <= 35, "19-35")
                 .when(year(current_date()) - year(col("birth_date")) <= 50, "36-50")
                 .when(year(current_date()) - year(col("birth_date")) <= 65, "51-65")
                 .otherwise("65+")
            ).otherwise("unknown")
        )
        .groupBy("age_group")
        .agg(count("*").alias("count"))
        .orderBy("age_group")
    )


def disorder_prevalence(inferences: DataFrame, disorders: DataFrame) -> DataFrame:
    return (
        inferences.join(disorders, "disorder_id")
        .groupBy("disorder_name", "cid_code")
        .agg(
            count("*").alias("inference_count"),
            round(avg("inference_probability"), 4).alias("avg_probability"),
            round(stddev("inference_probability"), 4).alias("std_probability"),
        )
        .orderBy(desc("inference_count"))
    )


def scale_statistics(scale_responses: DataFrame, questions: DataFrame, scales: DataFrame) -> DataFrame:
    return (
        scale_responses.join(questions, "question_id")
        .join(scales, "scale_id")
        .groupBy("scale_name")
        .agg(
            count("*").alias("total_responses"),
            round(avg("response_value"), 2).alias("avg_score"),
            round(stddev("response_value"), 2).alias("std_score"),
        )
        .orderBy("scale_name")
    )


def run_population_metrics() -> dict:
    spark = create_session()
    try:
        profiles = load_table(spark, "clinical.patient_profile")
        inferences = load_table(spark, "diagnostic.diagnostic_inference")
        disorders = load_table(spark, "diagnostic.disorders")
        scale_responses = load_table(spark, "clinical.scale_responses")
        questions = load_table(spark, "diagnostic.scale_questions")
        scales = load_table(spark, "diagnostic.assessment_scales")

        age_dist = age_distribution(profiles)
        prev = disorder_prevalence(inferences, disorders)
        scale_stats = scale_statistics(scale_responses, questions, scales)

        age_data = {r["age_group"]: int(r["count"]) for r in age_dist.collect()}
        prev_data = [
            {
                "disorder": r["disorder_name"],
                "cid": r["cid_code"],
                "count": int(r["inference_count"]),
                "avg_prob": float(r["avg_probability"]),
                "std_prob": float(r["std_probability"]),
            }
            for r in prev.collect()
        ]
        scale_data = [
            {
                "scale": r["scale_name"],
                "responses": int(r["total_responses"]),
                "avg": float(r["avg_score"]),
                "std": float(r["std_score"]),
            }
            for r in scale_stats.collect()
        ]

        total_patients = profiles.count()
        total_inferences = inferences.count()

        return {
            "total_patients": total_patients,
            "total_inferences": total_inferences,
            "age_distribution": age_data,
            "disorder_prevalence": prev_data,
            "scale_statistics": scale_data,
        }
    finally:
        spark.stop()


if __name__ == "__main__":
    result = run_population_metrics()
    print(f"Population metrics: {result}")
