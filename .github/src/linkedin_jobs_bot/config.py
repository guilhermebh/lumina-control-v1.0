from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BotConfig:
    keywords: list[str]
    locations: list[str]
    search_url: str
    profile_dir: str
    headless: bool
    scroll_rounds: int
    max_cards: int
    notify: bool
    notify_max_jobs: int
    telegram_bot_token: str
    telegram_chat_id: str
    discord_webhook_url: str
    output_dir: str
    state_filename: str
    json_filename: str
    csv_filename: str
    html_snapshot_filename: str

    @classmethod
    def from_file(cls, path: str | Path) -> "BotConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            keywords=[item.strip().lower() for item in data.get("keywords", []) if item.strip()],
            locations=[item.strip().lower() for item in data.get("locations", []) if item.strip()],
            search_url=data.get("search_url", "").strip(),
            profile_dir=data.get("profile_dir", ".playwright/linkedin-profile"),
            headless=bool(data.get("headless", False)),
            scroll_rounds=max(1, int(data.get("scroll_rounds", 8))),
            max_cards=max(1, int(data.get("max_cards", 100))),
            notify=bool(data.get("notify", True)),
            notify_max_jobs=max(1, int(data.get("notify_max_jobs", 10))),
            telegram_bot_token=data.get("telegram_bot_token", "").strip(),
            telegram_chat_id=data.get("telegram_chat_id", "").strip(),
            discord_webhook_url=data.get("discord_webhook_url", "").strip(),
            output_dir=data.get("output_dir", "output"),
            state_filename=data.get("state_filename", "seen_jobs.json"),
            json_filename=data.get("json_filename", "jobs.json"),
            csv_filename=data.get("csv_filename", "jobs.csv"),
            html_snapshot_filename=data.get("html_snapshot_filename", "linkedin-search-snapshot.html"),
        )
