"""
Import shim — re-exports from canonical bayesian_network module.
Use `from app.ml.inference.bayesian_network import ...` directly.
"""
from app.ml.inference.bayesian_network import (  # noqa: F401
    BayesianNetwork,
    BayesianNode,
    CPTEntry,
    InferenceEvidence,
    BayesianInferenceResult,
    wilson_interval,
)
