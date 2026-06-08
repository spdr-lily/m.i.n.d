from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    db.rollback()
    rows = db.execute(
        text("SELECT table_schema, table_name FROM information_schema.tables "
             "WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast') "
             "ORDER BY table_schema, table_name")
    ).fetchall()
    for r in rows:
        count = db.execute(text(f"SELECT COUNT(*) FROM {r[0]}.{r[1]}")).scalar()  # nosec - script tool
        print(f"{r[0]}.{r[1]}: {count}")
except Exception as e:
    print(f"ERRO: {e}")
finally:
    db.close()
