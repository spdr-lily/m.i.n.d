"""Model definitions: Logistic Regression, Random Forest, XGBoost."""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

ESTIMATORS = {
    "logistic_regression": {
        "class": LogisticRegression,
        "default_params": {
            "max_iter": 5000,
            "C": 1.0,
            "solver": "lbfgs",
            "class_weight": "balanced",
            "random_state": 42,
        },
        "tune_params": {
            "C": [0.01, 0.1, 1.0, 10.0],
            "max_iter": [1000, 2000, 5000],
        },
        "is_classifier": True,
    },
    "random_forest": {
        "class": RandomForestClassifier,
        "default_params": {
            "n_estimators": 200,
            "max_depth": 10,
            "min_samples_leaf": 4,
            "class_weight": "balanced",
            "random_state": 42,
            "n_jobs": -1,
        },
        "tune_params": {
            "n_estimators": [100, 200, 300],
            "max_depth": [5, 10, 15, None],
            "min_samples_leaf": [2, 4, 8],
        },
        "is_classifier": True,
    },
    "xgboost": {
        "class": XGBClassifier,
        "default_params": {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "eval_metric": "logloss",
            "random_state": 42,
            "verbosity": 0,
            "use_label_encoder": False,
        },
        "tune_params": {
            "n_estimators": [100, 200, 300],
            "max_depth": [4, 6, 8],
            "learning_rate": [0.01, 0.1, 0.2],
            "subsample": [0.7, 0.8, 1.0],
        },
        "is_classifier": True,
    },
}
