#!/usr/bin/env python
"""
Submit PySpark jobs for the M.I.N.D CDSS.

Usage:
    python spark/submit.py batch_inference
    python spark/submit.py population_metrics
    python spark/submit.py data_import --csv data/patients.csv
"""
import sys
import argparse
from spark.jobs import batch_inference, population_metrics, data_import


def main():
    parser = argparse.ArgumentParser(description="Submit M.I.N.D Spark job")
    parser.add_argument("job", choices=["batch_inference", "population_metrics", "data_import"])
    parser.add_argument("--csv", help="CSV file path for data import")
    args = parser.parse_args()

    if args.job == "batch_inference":
        result = batch_inference.run_batch_inference()
        print(f"Batch inference complete: {result}")

    elif args.job == "population_metrics":
        result = population_metrics.run_population_metrics()
        print(f"Population metrics: {result}")

    elif args.job == "data_import":
        if not args.csv:
            print("Error: --csv path required for data_import")
            sys.exit(1)
        result = data_import.import_patients_from_csv(None, args.csv)
        print(f"Import complete: {result}")


if __name__ == "__main__":
    main()
