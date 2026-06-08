"""
Import shim — re-exports from canonical disorder_predictor module.
Use `from app.ml.inference.disorder_predictor import DisorderPredictor` directly.
"""
from app.ml.inference.disorder_predictor import (  # noqa: F401
    DisorderPredictor,
    BayesianInferenceResult,
    InferenceEvidence,
    SYMPTOM_TO_NODE,
    DISORDER_NAME_REVERSE,
)
