from __future__ import annotations

import json
import re
from html import unescape
from pathlib import Path

from linkedin_jobs_bot.models import JobPosting


JSON_BLOCK_PATTERN = re.compile(r"<code[^>]*>(.*?)</code>", re.IGNORECASE | re.DOTALL)
URL_PATTERN = re.compile(r"https://www\.linkedin\.com/jobs/view/[^\"'&<\s]+", re.IGNORECASE)


def parse_jobs_from_html(path: str | Path) -> list[JobPosting]:
    raw_html = Path(path).read_text(encoding="utf-8", errors="ignore")
    jobs = _parse_from_json_blocks(raw_html, str(path))
    if jobs:
        return _deduplicate(jobs)
    return _deduplicate(_parse_from_html_fallback(raw_html, str(path)))


def _parse_from_json_blocks(raw_html: str, source_file: str) -> list[JobPosting]:
    jobs: list[JobPosting] = []

    for match in JSON_BLOCK_PATTERN.findall(raw_html):
        text = unescape(match).strip()
        if '"title"' not in text or '"companyName"' not in text:
            continue

        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue

        items = payload if isinstance(payload, list) else [payload]
        for item in items:
            if not isinstance(item, dict):
                continue
            title = _clean(item.get("title"))
            company = _clean(item.get("companyName") or item.get("companyDetails", {}).get("company"))
            location = _clean(item.get("formattedLocation") or item.get("location"))
            url = _clean(item.get("jobPostingUrl") or item.get("dashEntityUrn") or "")
            if url and url.startswith("urn:li:fsd_jobPosting:"):
                job_id = url.rsplit(":", 1)[-1]
                url = f"https://www.linkedin.com/jobs/view/{job_id}/"
            if title and company:
                jobs.append(
                    JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        source_file=source_file,
                    )
                )
    return jobs


def _parse_from_html_fallback(raw_html: str, source_file: str) -> list[JobPosting]:
    jobs: list[JobPosting] = []
    title_matches = re.findall(
        r'job-card-list__title[^>]*>(.*?)</a>',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    company_matches = re.findall(
        r'job-card-container__company-name[^>]*>(.*?)</span>',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    location_matches = re.findall(
        r'job-card-container__metadata-item[^>]*>(.*?)</li>',
        raw_html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    url_matches = URL_PATTERN.findall(raw_html)

    count = max(len(title_matches), len(company_matches), len(location_matches), len(url_matches))
    for index in range(count):
        title = _strip_tags(title_matches[index]) if index < len(title_matches) else ""
        company = _strip_tags(company_matches[index]) if index < len(company_matches) else ""
        location = _strip_tags(location_matches[index]) if index < len(location_matches) else ""
        url = url_matches[index] if index < len(url_matches) else ""

        if title and company:
            jobs.append(
                JobPosting(
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    source_file=source_file,
                )
            )

    return jobs


def _strip_tags(value: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", value)
    return _clean(cleaned)


def _clean(value: object) -> str:
    if value is None:
        return ""
    text = unescape(str(value))
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:
    unique: dict[tuple[str, str, str], JobPosting] = {}
    for job in jobs:
        key = (job.title.lower(), job.company.lower(), job.url.lower())
        unique[key] = job
    return list(unique.values())
