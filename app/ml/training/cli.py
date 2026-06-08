"""CLI entry point for model training."""

import argparse
import sys
from app.ml.training.trainer import Trainer
from app.ml.training.label_builder import LABEL_BUILDERS
from app.ml.training.estimators import ESTIMATORS


def main():
    parser = argparse.ArgumentParser(description="M.I.N.D ML Training Pipeline")
    parser.add_argument("--objective", "-o", required=True,
                        choices=list(LABEL_BUILDERS.keys()),
                        help="Prediction objective")
    parser.add_argument("--algorithm", "-a", required=True,
                        choices=list(ESTIMATORS.keys()),
                        help="ML algorithm")
    parser.add_argument("--tune", action="store_true",
                        help="Enable hyperparameter tuning via cross-validation")
    parser.add_argument("--description", "-d", default="",
                        help="Model description")
    parser.add_argument("--test-size", type=float, default=0.25,
                        help="Test set proportion")
    parser.add_argument("--cv-folds", type=int, default=5,
                        help="Cross-validation folds")

    args = parser.parse_args()

    trainer = Trainer()
    result = trainer.train(
        objective=args.objective,
        algorithm=args.algorithm,
        tune=args.tune,
        description=args.description or f"{args.objective} with {args.algorithm}",
        test_size=args.test_size,
        cv_folds=args.cv_folds,
    )

    print(f"\nTraining complete: {result['model_name']} v{result['version']}")
    print(f"  Run ID:  {result['run_id']}")
    print(f"  F1:      {result['metrics'].get('f1_score', 'N/A')}")
    print(f"  Acc:     {result['metrics'].get('accuracy', 'N/A')}")

    return result


if __name__ == "__main__":
    sys.exit(main())
