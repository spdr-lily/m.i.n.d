"""Export feature matrix to CSV for DVC versioning."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from app.core.config import settings
from app.ml.training.feature_engineering import build_feature_matrix
from app.ml.training.label_builder import LABEL_BUILDERS, TARGET_COLUMNS
from sqlalchemy import create_engine


def export():
    engine = create_engine(settings.database_url)
    df, feature_cols = build_feature_matrix(engine)

    for objective, builder in LABEL_BUILDERS.items():
        df_labeled = builder(df.copy())
        label_col = TARGET_COLUMNS[objective]
        df_labeled = df_labeled.dropna(subset=[label_col])

        out_path = f"data/datasets/features_{objective}.csv"
        cols = ["consultation_uuid", "patient_uuid", "consultation_date"] + feature_cols + [label_col]
        cols = [c for c in cols if c in df_labeled.columns]
        df_labeled[cols].to_csv(out_path, index=False)
        print(f"Exported {len(df_labeled)} rows -> {out_path}")

    print(f"\nFeature columns ({len(feature_cols)}): {feature_cols}")


if __name__ == "__main__":
    export()
