from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import joblib

from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.evaluate import evaluate
from sentinel_ml.models.registry import available_models


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="synthetic")
    parser.add_argument("--models", default="logistic_regression,random_forest,isolation_forest")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    rows = generate_rows(SyntheticConfig(rows=8000)) if args.dataset == "synthetic" else []
    run_id = uuid.uuid4().hex[:12]
    root = Path(__file__).resolve().parents[2]
    report_dir = Path(args.output_dir) if args.output_dir else root / "reports" / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate(rows, [name.strip() for name in args.models.split(",") if name.strip()])
    registry = available_models()
    best_name = str(result["best_model"])
    fitted_model = registry[best_name]().fit(rows)
    bundle_path = report_dir / "model_bundle.joblib"
    joblib.dump(
        {
            "model": fitted_model,
            "metrics": result["models"][best_name],  # type: ignore[index]
            "dataset": args.dataset,
            "run_id": run_id,
        },
        bundle_path,
    )
    if args.output_dir:
        # A stable filename lets the API swap in a newly trained bundle atomically.
        stable_path = report_dir / "model_bundle.joblib"
        if bundle_path != stable_path:
            bundle_path.replace(stable_path)
    (report_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    best = result["models"][best_name]  # type: ignore[index]
    (report_dir / "report.md").write_text(
        "# Sentinel Training Report\n\n"
        "Research / demo project. Not certified for production fraud prevention.\n\n"
        f"Dataset: {args.dataset}\n\n"
        f"Best model: `{best_name}`\n\n"
        f"Bundle: `{bundle_path.name}`\n\n"
        f"Chosen threshold: `{best['metrics']['threshold']}`\n\n"
        "Primary metrics:\n\n"
        f"- PR-AUC: `{best['metrics']['pr_auc']}`\n"
        f"- Recall @ precision 0.7: `{best['metrics']['recall_at_precision_0_7']}`\n"
        f"- Cost-weighted loss: `{best['metrics']['cost_weighted_loss']}`\n\n"
        f"Full metrics:\n\n```json\n{json.dumps(result, indent=2)}\n```\n",
        encoding="utf-8",
    )
    print(report_dir)


if __name__ == "__main__":
    main()
