import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:137_Cmspelo@localhost:5432/mind")
JDBC_URL = f"jdbc:postgresql://localhost:5432/mind"
DB_PROPERTIES = {
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "137_Cmspelo"),
    "driver": "org.postgresql.Driver",
}
SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]")
BATCH_SIZE = int(os.getenv("SPARK_BATCH_SIZE", "1000"))
