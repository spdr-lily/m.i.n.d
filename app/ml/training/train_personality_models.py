"""Training script for personality prediction models from scale scores."""

import json
import os
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

import joblib
import mlflow
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sqlalchemy import create_engine, text

from app.core.config import settings
from app.ml.registry.model_registry import ModelRegistry
from app.ml.registry.experiment_tracking import ExperimentTracker
from app.ml.training.feature_engineering import build_feature_matrix

PERSONALITY_OBJECTIVES = {
    "personality_bfp": {
        "targets": [
            "bfp_abertura", "bfp_conscienciosidade", "bfp_extroversao",
            "bfp_amabilidade", "bfp_neuroticismo",
        ],
        "description": "BFP 5-factor personality prediction from clinical scales",
    },
    "personality_dt12": {
        "targets": [
            "dt12_maquiavelismo", "dt12_narcisismo", "dt12_psicopatia",
        ],
        "description": "DT-12 Dark Triad prediction from clinical scales",
    },
}

ALGORITHMS = {
    "random_forest": {
        "class": RandomForestRegressor,
        "default_params": {
            "n_estimators": 200,
            "max_depth": 15,
            "min_samples_leaf": 4,
            "random_state": 42,
            "n_jobs": -1,
        },
    },
    "xgboost": {
        "class": None,
        "default_params": {},
    },
}


def get_personality_training_data(engine) -> pd.DataFrame:
    """Extract scale scores + personality factor data from DW for training."""
    query = """
    WITH scale_scores AS (
        SELECT
            c.consultation_uuid,
            pp.patient_uuid,
            s.scale_name,
            sum(sr.response_value) AS total_score
        FROM clinical.clinical_consultation c
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        JOIN clinical.scale_responses sr ON sr.consultation_uuid = c.consultation_uuid
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        GROUP BY c.consultation_uuid, pp.patient_uuid, s.scale_name
    ),
    clinical_pivot AS (
        SELECT consultation_uuid, patient_uuid,
            max(CASE WHEN scale_name='PHQ-9' THEN total_score END) AS phq9_score,
            max(CASE WHEN scale_name='GAD-7' THEN total_score END) AS gad7_score,
            max(CASE WHEN scale_name='MADRS' THEN total_score END) AS madrs_score,
            max(CASE WHEN scale_name='MDQ' THEN total_score END) AS mdq_score,
            max(CASE WHEN scale_name='PCL-5' THEN total_score END) AS pcl5_score,
            max(CASE WHEN scale_name='Y-BOCS' THEN total_score END) AS ybocs_score,
            max(CASE WHEN scale_name='AUDIT' THEN total_score END) AS audit_score,
            max(CASE WHEN scale_name='ASRM' THEN total_score END) AS asrm_score,
            max(CASE WHEN scale_name='ASRS' THEN total_score END) AS asrs_score,
            max(CASE WHEN scale_name='AQ-10' THEN total_score END) AS aq10_score,
            max(CASE WHEN scale_name='MEMÓRIA' THEN total_score END) AS memoria_score,
            max(CASE WHEN scale_name='QI - RASTREIO' THEN total_score END) AS qi_score,
            max(CASE WHEN scale_name='RECONHECIMENTO DE ROSTOS' THEN total_score END) AS reconhecimento_rostos_score
        FROM scale_scores
        GROUP BY consultation_uuid, patient_uuid
    ),
    bfp_scores AS (
        SELECT
            c.consultation_uuid,
            pp.patient_uuid,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Abertura -%') AS bfp_abertura,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Conscienciosidade -%') AS bfp_conscienciosidade,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Extroversão -%') AS bfp_extroversao,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Amabilidade -%') AS bfp_amabilidade,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Neuroticismo -%') AS bfp_neuroticismo
        FROM clinical.clinical_consultation c
        JOIN clinical.patient_profile pp ON c.profile_uuid = pp.profile_uuid
        JOIN clinical.scale_responses sr ON sr.consultation_uuid = c.consultation_uuid
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        WHERE s.scale_name = 'BFP'
        GROUP BY c.consultation_uuid, pp.patient_uuid
    ),
    dt12_scores AS (
        SELECT
            c.consultation_uuid,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Maquiavelismo -%') AS dt12_maquiavelismo,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Narcisismo -%') AS dt12_narcisismo,
            sum(sr.response_value) FILTER (WHERE sq.question_text LIKE 'Psicopatia -%') AS dt12_psicopatia
        FROM clinical.clinical_consultation c
        JOIN clinical.scale_responses sr ON sr.consultation_uuid = c.consultation_uuid
        JOIN diagnostic.scale_questions sq ON sr.question_id = sq.question_id
        JOIN diagnostic.assessment_scales s ON sq.scale_id = s.scale_id
        WHERE s.scale_name = 'DT-12 (Tríade Sombria)'
        GROUP BY c.consultation_uuid
    )
    SELECT cp.*,
           b.bfp_abertura, b.bfp_conscienciosidade, b.bfp_extroversao,
           b.bfp_amabilidade, b.bfp_neuroticismo,
           d.dt12_maquiavelismo, d.dt12_narcisismo, d.dt12_psicopatia
    FROM clinical_pivot cp
    LEFT JOIN bfp_scores b ON cp.consultation_uuid = b.consultation_uuid
    LEFT JOIN dt12_scores d ON cp.consultation_uuid = d.consultation_uuid
    """
    return pd.read_sql(text(query), engine)


def train_personality_model(
    objective: str,
    algorithm: str = "random_forest",
    db_url: str = "",
    mlflow_uri: str = "",
) -> dict:
    """Train a personality prediction model."""
    if objective not in PERSONALITY_OBJECTIVES:
        raise ValueError(f"Unknown objective: {objective}. Choose from {list(PERSONALITY_OBJECTIVES.keys())}")

    engine = create_engine(db_url or settings.database_url)
    tracker = ExperimentTracker(
        tracking_uri=mlflow_uri, experiment_name="mind-cdss-personality"
    )
    registry = ModelRegistry(engine)
    obj_def = PERSONALITY_OBJECTIVES[objective]
    target_cols = obj_def["targets"]

    # Feature columns: all clinical + neuro scale scores
    feature_cols = [
        "phq9_score", "gad7_score", "madrs_score", "mdq_score", "pcl5_score",
        "ybocs_score", "audit_score", "asrm_score", "asrs_score", "aq10_score",
        "memoria_score", "qi_score", "reconhecimento_rostos_score",
    ]

    model_name = f"{objective}_{algorithm}"

    with tracker.start_run(run_name=f"{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"):
        run = mlflow.active_run()
        run_id = run.info.run_id

        df = get_personality_training_data(engine)
        df = df.dropna(subset=target_cols)
        if df.empty:
            return {"run_id": run_id, "model_name": model_name, "version": 0, "metrics": {}, "params": {}}

        for c in feature_cols:
            if c not in df.columns:
                df[c] = 0.0
        X = df[feature_cols].fillna(0).values
        y = df[target_cols].fillna(0).values

        tracker.log_params({
            "objective": objective,
            "algorithm": algorithm,
            "n_samples": len(X),
            "n_features": len(feature_cols),
            "n_targets": len(target_cols),
            "targets": str(target_cols),
        })

        # Train model
        est_params = ALGORITHMS[algorithm]["default_params"]
        est_class = ALGORITHMS[algorithm]["class"]
        if est_class is None:
            from xgboost import XGBRegressor
            est_class = XGBRegressor
            est_params = {
                "n_estimators": 200,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": 42,
                "verbosity": 0,
            }
        base_model = est_class(**est_params)
        model = MultiOutputRegressor(base_model, n_jobs=-1)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Per-target metrics
        metrics = {}
        for i, col in enumerate(target_cols):
            mse = mean_squared_error(y_test[:, i], y_pred[:, i])
            mae = mean_absolute_error(y_test[:, i], y_pred[:, i])
            r2 = r2_score(y_test[:, i], y_pred[:, i])
            metrics[f"{col}_mse"] = round(float(mse), 4)
            metrics[f"{col}_mae"] = round(float(mae), 4)
            metrics[f"{col}_r2"] = round(float(r2), 4)

        # Overall metrics
        metrics["mean_mae"] = round(float(np.mean([
            mean_absolute_error(y_test[:, i], y_pred[:, i]) for i in range(len(target_cols))
        ])), 4)
        metrics["mean_r2"] = round(float(np.mean([
            r2_score(y_test[:, i], y_pred[:, i]) for i in range(len(target_cols))
        ])), 4)

        tracker.log_metrics(metrics)

        print(f"\n=== {model_name} ===")
        print(f"Run ID: {run_id}")
        print(f"Metrics: {json.dumps(metrics, indent=2)}")

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = os.path.join(tmpdir, model_name)
            artifact = {
                "model": model,
                "feature_cols": feature_cols,
                "target_names": target_cols,
                "objective": objective,
            }
            joblib.dump(artifact, model_path)
            mlflow.log_artifact(model_path, artifact_path="models")

            registered = registry.register_model(objective, algorithm, obj_def["description"])
            mv = registry.create_version(
                model_id=registered.model_id,
                mlflow_run_id=run_id,
                mlflow_model_uri=f"runs:/{run_id}/models/{model_name}",
                metrics=metrics,
                params=est_params,
                feature_list=feature_cols,
                train_size=len(X_train),
                test_size=len(X_test),
                artifact_path=f"models/{model_name}",
            )

            registry.promote_to_production(registered.model_id, mv.version)
            print(f"Registered {model_name} v{mv.version} in production")

        return {
            "run_id": run_id,
            "model_name": model_name,
            "version": mv.version,
            "metrics": metrics,
            "params": est_params,
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train personality prediction model")
    parser.add_argument("objective", choices=list(PERSONALITY_OBJECTIVES.keys()), help="Prediction objective")
    parser.add_argument("--algorithm", default="random_forest", choices=list(ALGORITHMS.keys()), help="ML algorithm")
    args = parser.parse_args()
    result = train_personality_model(args.objective, args.algorithm)
    print(json.dumps(result, indent=2, default=str))
