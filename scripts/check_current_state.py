from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("=== Disorders ===")
    rs = conn.execute(text("SELECT disorder_id, disorder_name, cid_code, dsm_code FROM diagnostic.disorders ORDER BY disorder_id"))
    for r in rs:
        icd11 = conn.execute(text("SELECT icd11_code FROM diagnostic.icd11_codes WHERE disorder_id = :did"), {"did": r[0]}).fetchone()
        icd = icd11[0] if icd11 else "-"
        print(f"  ID {r[0]}: {r[1]} (CID-10={r[2]}, DSM={r[3]}, CID-11={icd})")

    print("\n=== Inferences (consultations with disorder references) ===")
    rs = conn.execute(text("SELECT COUNT(*) FROM diagnostic.diagnostic_inference WHERE disorder_id IS NOT NULL"))
    print(f"  Total inference rows: {rs.scalar()}")
    rs = conn.execute(text("SELECT DISTINCT disorder_id FROM diagnostic.diagnostic_inference WHERE disorder_id IS NOT NULL ORDER BY disorder_id"))
    for r in rs:
        cnt = conn.execute(text("SELECT COUNT(*) FROM diagnostic.diagnostic_inference WHERE disorder_id = :did"), {"did": r[0]}).scalar()
        name = conn.execute(text("SELECT disorder_name FROM diagnostic.disorders WHERE disorder_id = :did"), {"did": r[0]}).scalar()
        print(f"  ID {r[0]} ({name}): {cnt} inferences")

    print("\n=== ICD-11 codes ===")
    rs = conn.execute(text("SELECT c.code_id, c.disorder_id, d.disorder_name, c.icd11_code FROM diagnostic.icd11_codes c JOIN diagnostic.disorders d ON d.disorder_id = c.disorder_id ORDER BY c.code_id"))
    for r in rs:
        print(f"  ID {r[0]}: disorder {r[1]} ({r[2]}) -> {r[3]}")

    print("\n=== Criteria groups ===")
    rs = conn.execute(text("SELECT g.group_id, g.disorder_id, d.disorder_name, g.group_label FROM diagnostic.criteria_groups g JOIN diagnostic.disorders d ON d.disorder_id = g.disorder_id ORDER BY g.group_id"))
    for r in rs:
        print(f"  ID {r[0]}: disorder {r[1]} ({r[2]}) group {r[3]}")
