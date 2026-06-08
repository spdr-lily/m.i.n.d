"""Data quality report: runs clinical integrity checks and outputs results."""
import json
import sys
from datetime import datetime
from app.core.database import SessionLocal
from app.services.integrity_service import ClinicalIntegrityService, INTEGRITY_ERROR, INTEGRITY_WARNING


def run_quality_report() -> dict:
    db = SessionLocal()
    try:
        svc = ClinicalIntegrityService(db)
        report = svc.full_report()
        return report
    finally:
        db.close()


def main():
    report = run_quality_report()
    all_items = (
        report["patients"]
        + report["consultations"]
        + report["inference_sets"]
    )
    errors = [i for i in all_items if i["severity"] == INTEGRITY_ERROR]
    warnings = [i for i in all_items if i["severity"] == INTEGRITY_WARNING]
    infos = [i for i in all_items if i["severity"] == "info"]

    report["summary"]["errors"] = len(errors)
    report["summary"]["warnings"] = len(warnings)
    report["summary"]["info"] = len(infos)

    print(f"{'='*60}")
    print(f"DATA QUALITY REPORT - {datetime.now().isoformat()}")
    print(f"{'='*60}")
    print(f"  Errors:   {len(errors)}")
    print(f"  Warnings: {len(warnings)}")
    print(f"  Info:     {len(infos)}")
    print(f"{'='*60}")

    for item in all_items:
        tag = {
            INTEGRITY_ERROR: "ERROR",
            INTEGRITY_WARNING: "WARN",
        }.get(item["severity"], "INFO")
        print(f"  [{tag:5s}] {item['entity']:25s} | {item['field']:30s} | {item['message']}")

    if not all_items:
        print("  No issues found.")

    output_path = "data/reports/clinical_integrity_report.json"
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    print(f"\nReport saved to {output_path}")
    return report


if __name__ == "__main__":
    sys.exit(0 if main()["summary"]["errors"] == 0 else 1)
