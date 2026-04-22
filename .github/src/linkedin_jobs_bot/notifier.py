from __future__ import annotations

import json
from urllib import error, parse, request

from linkedin_jobs_bot.config import BotConfig
from linkedin_jobs_bot.models import JobPosting


def send_notifications(jobs: list[JobPosting], config: BotConfig) -> list[str]:
    if not config.notify or not jobs:
        return []

    message = build_jobs_message(jobs, max_jobs=config.notify_max_jobs)
    delivered_to: list[str] = []

    if config.telegram_bot_token and config.telegram_chat_id:
        _send_telegram_message(
            bot_token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id,
            message=message,
        )
        delivered_to.append("telegram")

    if config.discord_webhook_url:
        _send_discord_message(
            webhook_url=config.discord_webhook_url,
            message=message,
        )
        delivered_to.append("discord")

    return delivered_to


def build_jobs_message(jobs: list[JobPosting], *, max_jobs: int) -> str:
    selected_jobs = jobs[:max_jobs]
    lines = [f"LinkedIn Jobs Bot encontrou {len(jobs)} vaga(s) filtrada(s).", ""]

    for index, job in enumerate(selected_jobs, start=1):
        lines.append(f"{index}. {job.title}")
        lines.append(f"Empresa: {job.company}")
        if job.location:
            lines.append(f"Local: {job.location}")
        if job.url:
            lines.append(f"Link: {job.url}")
        lines.append("")

    hidden_count = len(jobs) - len(selected_jobs)
    if hidden_count > 0:
        lines.append(f"E mais {hidden_count} vaga(s) no arquivo JSON/CSV.")

    return "\n".join(lines).strip()


def _send_telegram_message(*, bot_token: str, chat_id: str, message: str) -> None:
    encoded_message = parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    req = request.Request(url, data=encoded_message, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    _perform_request(req, "Telegram")


def _send_discord_message(*, webhook_url: str, message: str) -> None:
    payload = json.dumps({"content": message}).encode("utf-8")
    req = request.Request(webhook_url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    _perform_request(req, "Discord")


def _perform_request(req: request.Request, channel_name: str) -> None:
    try:
        with request.urlopen(req, timeout=20) as response:
            status = response.getcode()
            if status >= 400:
                raise RuntimeError(f"Falha ao enviar notificacao para {channel_name}: HTTP {status}")
    except error.HTTPError as exc:
        raise RuntimeError(
            f"Falha ao enviar notificacao para {channel_name}: HTTP {exc.code}"
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(
            f"Falha de rede ao enviar notificacao para {channel_name}: {exc.reason}"
        ) from exc
