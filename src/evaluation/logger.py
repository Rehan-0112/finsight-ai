"""
logger.py

Saves retrieval evaluation reports.
"""

import json
from pathlib import Path

def save_report(
    ticker: str,
    report: dict
) -> None:

    output_dir = Path("data") / "evaluation"

    output_dir.mkdir(parents=True, exist_ok=True)

    file = output_dir / f"{ticker}_evaluation.json"

    with open(file, "w", encoding="utf-8") as f:

        json.dump(report, f, indent=4)