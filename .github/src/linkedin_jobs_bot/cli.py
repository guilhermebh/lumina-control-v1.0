from __future__ import annotations

import argparse

from linkedin_jobs_bot.collector import collect_jobs_with_playwright
from linkedin_jobs_bot.config import BotConfig
from linkedin_jobs_bot.models import JobPosting
from linkedin_jobs_bot.notifier import send_notifications
from linkedin_jobs_bot.parser import parse_jobs_from_html
from linkedin_jobs_bot.state import get_new_jobs, job_key, load_seen_job_keys, save_seen_job_keys
from linkedin_jobs_bot.storage import save_html_snapshot, save_jobs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrai e filtra vagas do LinkedIn por HTML salvo ou coleta com Playwright."
    )
    parser.add_argument("--config", required=True, help="Arquivo JSON com filtros e destino de saida.")
    parser.add_argument("--input", nargs="+", help="Um ou mais arquivos HTML salvos.")
    parser.add_argument(
        "--collect",
        action="store_true",
        help="Abre o LinkedIn Jobs com Playwright e coleta as vagas visiveis.",
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="Executa normalmente, mas nao envia alertas para Telegram ou Discord.",
    )
    parser.add_argument(
        "--reset-seen",
        action="store_true",
        help="Ignora o historico de vagas vistas nesta execucao e recria o estado ao final.",
    )
    args = parser.parse_args()

    config = BotConfig.from_file(args.config)
    if not args.collect and not args.input:
        parser.error("Informe --collect ou pelo menos um arquivo com --input.")
    if args.no_notify:
        config = _copy_config_with_notify_disabled(config)

    jobs: list[JobPosting] = []
    snapshot_path = None

    if args.collect:
        collected_jobs, html_snapshot = collect_jobs_with_playwright(
            search_url=config.search_url,
            profile_dir=config.profile_dir,
            headless=config.headless,
            scroll_rounds=config.scroll_rounds,
            max_cards=config.max_cards,
        )
        jobs.extend(collected_jobs)
        snapshot_path = save_html_snapshot(
            html_snapshot,
            output_dir=config.output_dir,
            filename=config.html_snapshot_filename,
        )

    if args.input:
        for input_path in args.input:
            jobs.extend(parse_jobs_from_html(input_path))

    jobs = _deduplicate(jobs)
    filtered_jobs = _filter_jobs(jobs, config)
    seen_job_keys = set() if args.reset_seen else load_seen_job_keys(config.output_dir, config.state_filename)
    new_jobs = get_new_jobs(filtered_jobs, seen_job_keys)
    json_path, csv_path = save_jobs(
        filtered_jobs,
        output_dir=config.output_dir,
        json_filename=config.json_filename,
        csv_filename=config.csv_filename,
    )
    updated_seen_job_keys = set(seen_job_keys)
    updated_seen_job_keys.update(job_key(job) for job in filtered_jobs)
    state_path = save_seen_job_keys(updated_seen_job_keys, config.output_dir, config.state_filename)

    print(f"Arquivos processados: {len(args.input or [])}")
    print(f"Coleta Playwright ativa: {'sim' if args.collect else 'nao'}")
    print(f"Vagas extraidas: {len(jobs)}")
    print(f"Vagas apos filtro: {len(filtered_jobs)}")
    print(f"Vagas novas nesta execucao: {len(new_jobs)}")
    print(f"JSON salvo em: {json_path}")
    print(f"CSV salvo em: {csv_path}")
    print(f"Estado salvo em: {state_path}")
    if snapshot_path is not None:
        print(f"Snapshot HTML salvo em: {snapshot_path}")
    delivered_to = send_notifications(new_jobs, config)
    if delivered_to:
        print(f"Notificacoes enviadas para: {', '.join(delivered_to)}")
    else:
        print("Notificacoes enviadas para: nenhum canal")
    return 0


def _filter_jobs(jobs: list[JobPosting], config: BotConfig) -> list[JobPosting]:
    results: list[JobPosting] = []
    for job in jobs:
        search_blob = " ".join([job.title, job.company, job.location]).lower()
        keyword_match = not config.keywords or any(term in search_blob for term in config.keywords)
        location_match = not config.locations or any(term in job.location.lower() for term in config.locations)
        if keyword_match and location_match:
            results.append(job)
    return results


def _deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:
    seen: dict[tuple[str, str, str], JobPosting] = {}
    for job in jobs:
        key = (job.title.lower(), job.company.lower(), job.url.lower())
        seen[key] = job
    return list(seen.values())


def _copy_config_with_notify_disabled(config: BotConfig) -> BotConfig:
    return BotConfig(
        keywords=config.keywords,
        locations=config.locations,
        search_url=config.search_url,
        profile_dir=config.profile_dir,
        headless=config.headless,
        scroll_rounds=config.scroll_rounds,
        max_cards=config.max_cards,
        notify=False,
        notify_max_jobs=config.notify_max_jobs,
        telegram_bot_token=config.telegram_bot_token,
        telegram_chat_id=config.telegram_chat_id,
        discord_webhook_url=config.discord_webhook_url,
        output_dir=config.output_dir,
        state_filename=config.state_filename,
        json_filename=config.json_filename,
        csv_filename=config.csv_filename,
        html_snapshot_filename=config.html_snapshot_filename,
    )
