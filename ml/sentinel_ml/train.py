from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from sentinel_ml.data.synthetic import SyntheticConfig, generate_rows
from sentinel_ml.evaluate import evaluate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="synthetic")
    args = parser.parse_args()
    rows = generate_rows(SyntheticConfig(rows=5000)) if args.dataset == "synthetic" else []
    run_id = uuid.uuid4().hex[:12]
    root = Path(__file__).resolve().parents[2]
    report_dir = root / "reports" / run_id
    report_dir.mkdir(parents=True, exist_ok=True)
    result = evaluate(rows)
    (report_dir / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (report_dir / "report.md").write_text(
        "# Sentinel Training Report\n\n"
        "Research / demo project. Not certified for production fraud prevention.\n\n"
        f"Dataset: {args.dataset}\n\n"
        f"Metrics:\n\n```json\n{json.dumps(result, indent=2)}\n```\n",
        encoding="utf-8",
    )
    print(report_dir)


if __name__ == "__main__":
    main()

