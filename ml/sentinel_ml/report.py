from __future__ import annotations

from pathlib import Path


def main() -> None:
    reports = sorted((Path(__file__).resolve().parents[2] / "reports").glob("*/report.md"))
    if not reports:
        print("No reports found. Run `make train` first.")
        return
    print(reports[-1])


if __name__ == "__main__":
    main()

