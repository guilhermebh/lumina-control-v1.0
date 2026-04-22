from __future__ import annotations

import csv
import json
from pathlib import Path

from linkedin_jobs_bot.models import JobPosting


def save_jobs(jobs: list[JobPosting], output_dir: str, json_filename: str, csv_filename: str) -> tuple[Path, Path]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / json_filename
    csv_path = output_path / csv_filename

    json_path.write_text(
        json.dumps([job.to_dict() for job in jobs], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["title", "company", "location", "url", "source_file"],
        )
        writer.writeheader()
        for job in jobs:
            writer.writerow(job.to_dict())

    return json_path, csv_path


def save_html_snapshot(html: str, output_dir: str, filename: str) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    html_path = output_path / filename
    html_path.write_text(html, encoding="utf-8")
    return html_path
