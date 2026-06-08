"""Prediction service: loads production model and makes predictions."""

import json
import joblib
import mlflow
import numpy as np
import pandas as pd
from typing import Optional
from sqlalchemy import create_engine

from app.core.config import settings
from app.ml.registry.model_registry import ModelRegistry
from app.ml.training.feature_engineering import build_feature_matrix


class PredictorService:

    def __init__(self, db_url: str = ""):
        self.db_url = db_url or settings.database_url
        self.engine = create_engine(self.db_url)
        self.registry = ModelRegistry(self.engine)
        self._models = {}

    def _load_model(self, objective: str, algorithm: str):
        key = f"{objective}_{algorithm}"
        if key in self._models:
            return self._models[key]

        mv = self.registry.get_production_model(objective, algorithm)
        if mv is None:
            mv = self.registry.get_best_version(objective, algorithm)
        if mv is None:
            raise ValueError(f"No trained model found for {objective}/{algorithm}")

        model_uri = mv.mlflow_model_uri
        local = mlflow.artifacts.download_artifacts(model_uri)
        artifact = joblib.load(local)
        self._models[key] = artifact
        return artifact

    def predict(self, objective: str, algorithm: str = "random_forest") -> dict:
        artifact = self._load_model(objective, algorithm)
        model = artifact["model"]
        le = artifact["label_encoder"]
        feature_cols = artifact["feature_cols"]

        df, _ = build_feature_matrix(self.engine)
        df = df.dropna(subset=feature_cols)
        X = df[feature_cols].values

        y_pred = model.predict(X)
        y_proba = model.predict_proba(X) if hasattr(model, "predict_proba") else None

        results = []
        for i in range(len(df)):
            row = df.iloc[i]
            pred_class = le.inverse_transform([y_pred[i]])[0]
            proba = y_proba[i].tolist() if y_proba is not None else []
            proba_dict = {}
            for j, cls_name in enumerate(le.classes_):
                proba_dict[cls_name] = round(float(y_proba[i][j]), 4) if y_proba is not None else None

            results.append({
                "consultation_uuid": str(row.get("consultation_uuid", "")),
                "patient_uuid": str(row.get("patient_uuid", "")),
                "prediction": pred_class,
                "probabilities": proba_dict,
                "confidence": round(float(max(y_proba[i])) if y_proba is not None else 0, 4),
            })

        return {
            "objective": objective,
            "algorithm": algorithm,
            "n_predictions": len(results),
            "predictions": results,
        }

    def predict_single(
        self, objective: str, consultation_uuid: str, algorithm: str = "random_forest"
    ) -> Optional[dict]:
        artifact = self._load_model(objective, algorithm)
        model = artifact["model"]
        le = artifact["label_encoder"]
        feature_cols = artifact["feature_cols"]

        df, _ = build_feature_matrix(self.engine)
        row = df[df["consultation_uuid"].astype(str) == consultation_uuid]
        if row.empty:
            return None

        X = row[feature_cols].fillna(0).values
        y_pred = model.predict(X)
        y_proba = model.predict_proba(X)

        pred_class = le.inverse_transform(y_pred)[0]
        proba_dict = {}
        for j, cls_name in enumerate(le.classes_):
            proba_dict[cls_name] = round(float(y_proba[0][j]), 4)

        return {
            "consultation_uuid": consultation_uuid,
            "prediction": pred_class,
            "probabilities": proba_dict,
            "confidence": round(float(max(y_proba[0])), 4),
        }
