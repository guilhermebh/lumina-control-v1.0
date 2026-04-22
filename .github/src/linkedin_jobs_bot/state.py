from __future__ import annotations

import hashlib
import json
from pathlib import Path

from linkedin_jobs_bot.models import JobPosting


def load_seen_job_keys(output_dir: str, state_filename: str) -> set[str]:
    state_path = Path(output_dir) / state_filename
    if not state_path.exists():
        return set()

    data = json.loads(state_path.read_text(encoding="utf-8"))
    items = data.get("seen_job_keys", [])
    return {str(item) for item in items}


def save_seen_job_keys(job_keys: set[str], output_dir: str, state_filename: str) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    state_path = output_path / state_filename
    payload = {"seen_job_keys": sorted(job_keys)}
    state_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return state_path


def job_key(job: JobPosting) -> str:
    source = "||".join(
        [
            job.title.strip().lower(),
            job.company.strip().lower(),
            job.location.strip().lower(),
            job.url.strip().lower(),
        ]
    )
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def get_new_jobs(jobs: list[JobPosting], seen_job_keys: set[str]) -> list[JobPosting]:
    return [job for job in jobs if job_key(job) not in seen_job_keys]
