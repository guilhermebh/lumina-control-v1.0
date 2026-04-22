from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class JobPosting:
    title: str
    company: str
    location: str
    url: str
    source_file: str

    def to_dict(self) -> dict:
        return asdict(self)
