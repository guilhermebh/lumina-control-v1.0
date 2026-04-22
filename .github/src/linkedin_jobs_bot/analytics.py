from __future__ import annotations

from collections import Counter

from linkedin_jobs_bot.models import JobPosting


REMOTE_KEYWORDS = {
    "remote",
    "remoto",
    "home office",
    "work from home",
    "anywhere",
}

HYBRID_KEYWORDS = {
    "hybrid",
    "hibrido",
    "híbrido",
    "flexible",
    "flexivel",
    "flexível",
}

ONSITE_KEYWORDS = {
    "on-site",
    "onsite",
    "presencial",
    "in office",
    "office-based",
}


def classify_work_mode(job: JobPosting) -> str:
    searchable = " ".join([job.title, job.location, job.source_file]).lower()

    if any(keyword in searchable for keyword in HYBRID_KEYWORDS):
        return "hybrid"
    if any(keyword in searchable for keyword in REMOTE_KEYWORDS):
        return "remote"
    if any(keyword in searchable for keyword in ONSITE_KEYWORDS):
        return "onsite"
    return "unknown"


def summarize_jobs(jobs: list[JobPosting]) -> dict:
    mode_counter = Counter(classify_work_mode(job) for job in jobs)
    company_counter = Counter(job.company for job in jobs if job.company)
    location_counter = Counter(job.location for job in jobs if job.location)

    return {
        "totals": {
            "all": len(jobs),
            "remote": mode_counter.get("remote", 0),
            "hybrid": mode_counter.get("hybrid", 0),
            "onsite": mode_counter.get("onsite", 0),
            "unknown": mode_counter.get("unknown", 0),
        },
        "top_companies": _serialize_counter(company_counter, 8),
        "top_locations": _serialize_counter(location_counter, 8),
    }


def serialize_jobs(jobs: list[JobPosting]) -> list[dict]:
    return [
        {
            **job.to_dict(),
            "work_mode": classify_work_mode(job),
        }
        for job in jobs
    ]


def _serialize_counter(counter: Counter, limit: int) -> list[dict]:
    return [
        {"label": label, "count": count}
        for label, count in counter.most_common(limit)
    ]
