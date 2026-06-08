"""MLflow experiment tracking wrapper."""

import os
import mlflow
from typing import Optional
from mlflow.tracking import MlflowClient


class ExperimentTracker:

    def __init__(self, tracking_uri: str = "", experiment_name: str = "mind-cdss"):
        self.tracking_uri = tracking_uri or os.getenv(
            "MLFLOW_TRACKING_URI", "sqlite:///mlflow.db"
        )
        mlflow.set_tracking_uri(self.tracking_uri)
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.client = MlflowClient(tracking_uri=self.tracking_uri)

    def start_run(self, run_name: str = "", nested: bool = False):
        return mlflow.start_run(run_name=run_name, nested=nested)

    def log_params(self, params: dict):
        mlflow.log_params(params)

    def log_metrics(self, metrics: dict, step: Optional[int] = None):
        mlflow.log_metrics(metrics, step=step)

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        mlflow.log_artifact(local_path, artifact_path=artifact_path)

    def log_model(self, model, artifact_path: str, **kwargs):
        mlflow.sklearn.log_model(model, artifact_path=artifact_path, **kwargs)

    def register_model(self, model_uri: str, name: str):
        return mlflow.register_model(model_uri, name)

    def get_run(self, run_id: str):
        return self.client.get_run(run_id)

    def search_runs(self, experiment_ids=None, filter_string=""):
        return mlflow.search_runs(experiment_ids, filter_string)

    @staticmethod
    def get_active_run():
        return mlflow.active_run()

    @staticmethod
    def end_run():
        mlflow.end_run()
