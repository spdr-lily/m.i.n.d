"""Train all 12 model combinations (4 objectives × 3 algorithms)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.ml.training.trainer import Trainer
from app.ml.training.label_builder import LABEL_BUILDERS
from app.ml.training.estimators import ESTIMATORS

OBJECTIVES = list(LABEL_BUILDERS.keys())
ALGORITHMS = list(ESTIMATORS.keys())

results = []
trainer = Trainer()

for objective in OBJECTIVES:
    for algorithm in ALGORITHMS:
        print(f"\n{'='*60}")
        print(f"Training: {objective} / {algorithm}")
        print(f"{'='*60}")
        try:
            result = trainer.train(
                objective=objective,
                algorithm=algorithm,
                tune=False,
                description=f"{objective} with {algorithm}",
            )
            results.append(result)
            f1 = result["metrics"].get("f1_score", "N/A")
            acc = result["metrics"].get("accuracy", "N/A")
            print(f"  OK {objective}/{algorithm} -- F1={f1}, Acc={acc}")
        except Exception as e:
            print(f"  FAIL {objective}/{algorithm} -- {e}")

print(f"\n{'='*60}")
print(f"Training complete: {len(results)}/{len(OBJECTIVES)*len(ALGORITHMS)} models")
print(f"{'='*60}")
for r in results:
    print(f"  {r['model_name']:50s} v{r['version']}  F1={r['metrics'].get('f1_score','?'):.4f}  Acc={r['metrics'].get('accuracy','?'):.4f}")
