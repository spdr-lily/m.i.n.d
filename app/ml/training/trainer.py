"""Training pipeline: feature extraction, label building, model training, MLflow tracking."""

import json
import os
import tempfile
from datetime import datetime
from typing import Optional

import mlflow
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    classification_report, confusion_matrix,
)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder

from app.core.config import settings
from app.ml.registry.model_registry import ModelRegistry
from app.ml.registry.experiment_tracking import ExperimentTracker
from app.ml.training.feature_engineering import build_feature_matrix
from app.ml.training.label_builder import LABEL_BUILDERS, TARGET_COLUMNS
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

ESTIMATORS = {
    "logistic_regression": {
        "class": LogisticRegression,
        "default_params": {"max_iter": 5000, "C": 1.0, "solver": "lbfgs", "class_weight": "balanced", "random_state": 42},
        "tune_params": {"C": [0.01, 0.1, 1.0, 10.0], "max_iter": [1000, 2000, 5000]},
        "is_classifier": True,
    },
    "random_forest": {
        "class": RandomForestClassifier,
        "default_params": {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 4, "class_weight": "balanced", "random_state": 42, "n_jobs": -1},
        "tune_params": {"n_estimators": [100, 200, 300], "max_depth": [5, 10, 15, None], "min_samples_leaf": [2, 4, 8]},
        "is_classifier": True,
    },
    "xgboost": {
        "class": XGBClassifier,
        "default_params": {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1, "subsample": 0.8, "colsample_bytree": 0.8, "eval_metric": "logloss", "random_state": 42, "verbosity": 0, "use_label_encoder": False},
        "tune_params": {"n_estimators": [100, 200, 300], "max_depth": [4, 6, 8], "learning_rate": [0.01, 0.1, 0.2], "subsample": [0.7, 0.8, 1.0]},
        "is_classifier": True,
    },
}
from sqlalchemy import create_engine


class Trainer:

    def __init__(
        self,
        db_url: str = "",
        mlflow_uri: str = "",
        experiment_name: str = "mind-cdss",
    ):
        self.db_url = db_url or settings.database_url
        self.engine = create_engine(self.db_url)
        self.tracker = ExperimentTracker(
            tracking_uri=mlflow_uri, experiment_name=experiment_name
        )
        self.registry = ModelRegistry(self.engine)

    def train(
        self,
        objective: str,
        algorithm: str,
        tune: bool = False,
        description: str = "",
        test_size: float = 0.25,
        cv_folds: int = 5,
    ):
        if objective not in LABEL_BUILDERS:
            raise ValueError(f"Unknown objective: {objective}. Choose from {list(LABEL_BUILDERS.keys())}")
        if algorithm not in ESTIMATORS:
            raise ValueError(f"Unknown algorithm: {algorithm}. Choose from {list(ESTIMATORS.keys())}")

        label_col = TARGET_COLUMNS[objective]
        label_builder = LABEL_BUILDERS[objective]
        est_def = ESTIMATORS[algorithm]
        model_name = f"{objective}_{algorithm}"

        with self.tracker.start_run(run_name=f"{model_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"):
            run = mlflow.active_run()
            run_id = run.info.run_id
            self.tracker.log_params({
                "objective": objective,
                "algorithm": algorithm,
                "test_size": test_size,
                "cv_folds": cv_folds,
                "tune": tune,
            })

            df, feature_cols = build_feature_matrix(self.engine)
            df_labeled = label_builder(df)

            df_labeled = df_labeled.dropna(subset=[label_col])
            y_raw = df_labeled[label_col].values

            le = LabelEncoder()
            y = le.fit_transform(y_raw)

            X = df_labeled[feature_cols].values
            n_classes = len(le.classes_)

            self.tracker.log_params({
                "n_samples": len(X),
                "n_features": len(feature_cols),
                "n_classes": n_classes,
                "classes": str(le.classes_.tolist()),
            })

            if tune:
                best_score = -1
                best_params = None
                best_model = None
                for param_combo in self._param_grid(est_def["tune_params"]):
                    model = est_def["class"](**{**est_def["default_params"], **param_combo})
                    scores = cross_val_score(
                        model, X, y, cv=StratifiedKFold(cv_folds, shuffle=True, random_state=42),
                        scoring="f1_macro",
                    )
                    mean_score = scores.mean()
                    if mean_score > best_score:
                        best_score = mean_score
                        best_params = param_combo
                        best_model = model
                params = {**est_def["default_params"], **best_params}
                model = best_model
            else:
                params = est_def["default_params"]
                model = est_def["class"](**params)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, stratify=y, random_state=42
            )

            # XGBoost: inject scale_pos_weight based on training distribution
            if algorithm == "xgboost":
                neg = (y_train == 0).sum()
                pos = (y_train == 1).sum()
                if pos > 0:
                    ratio = float(neg / pos)
                    model.set_params(scale_pos_weight=ratio)
                    params["scale_pos_weight"] = ratio

            self.tracker.log_params(params)

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None

            metrics = self._compute_metrics(y_test, y_pred, y_proba)
            self.tracker.log_metrics(metrics)
            self.tracker.log_params({
                "n_train": len(y_train),
                "n_test": len(y_test),
            })

            print(f"\n=== {model_name} ===")
            print(f"Run ID: {run_id}")
            print(f"Params: {json.dumps(params, default=str)}")
            print(f"Metrics: {json.dumps(metrics, default=str, indent=2)}")
            present_labels = sorted(set(y_test) | set(y_pred))
            target_names = [str(le.classes_[i]) for i in present_labels]
            print(f"\nClassification Report:\n{classification_report(y_test, y_pred, labels=present_labels, target_names=target_names)}")

            with tempfile.TemporaryDirectory() as tmpdir:
                model_path = os.path.join(tmpdir, model_name)
                import joblib
                joblib.dump({"model": model, "label_encoder": le, "feature_cols": feature_cols}, model_path)

                mlflow.log_artifact(model_path, artifact_path="models")

                registered = self.registry.register_model(objective, algorithm, description)
                mv = self.registry.create_version(
                    model_id=registered.model_id,
                    mlflow_run_id=run_id,
                    mlflow_model_uri=f"runs:/{run_id}/models/{model_name}",
                    metrics=metrics,
                    params={k: str(v) for k, v in params.items()},
                    feature_list=feature_cols,
                    train_size=len(y_train),
                    test_size=len(y_test),
                    artifact_path=f"models/{model_name}",
                )

                print(f"Registered model: {model_name} v{mv.version} (id={mv.version_id})")

                self.registry.promote_to_production(registered.model_id, mv.version)
                print(f"Promoted {model_name} v{mv.version} to production")

            return {
                "run_id": run_id,
                "model_name": model_name,
                "version": mv.version,
                "metrics": metrics,
                "params": params,
            }

    def _compute_metrics(self, y_true, y_pred, y_proba=None):
        metrics = {
            "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
            "precision_macro": round(float(precision_score(y_true, y_pred, average="macro", zero_division=0)), 4),
            "recall_macro": round(float(recall_score(y_true, y_pred, average="macro", zero_division=0)), 4),
            "f1_score": round(float(f1_score(y_true, y_pred, average="macro", zero_division=0)), 4),
        }
        if y_proba is not None and y_proba.shape[1] == 2:
            try:
                y_prob_pos = y_proba[:, 1]
                metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_prob_pos)), 4)
                metrics["pr_auc"] = round(float(average_precision_score(y_true, y_prob_pos)), 4)
                metrics["brier_score"] = round(float(brier_score_loss(y_true, y_prob_pos)), 4)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("Metrics calculation failed: %s", e)
        return metrics

    def _param_grid(self, tune_params: dict):
        from itertools import product
        keys = list(tune_params.keys())
        for values in product(*tune_params.values()):
            yield dict(zip(keys, values))
