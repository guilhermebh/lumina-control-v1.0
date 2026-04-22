from __future__ import annotations

from pathlib import Path

from linkedin_jobs_bot.models import JobPosting

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - depends on optional runtime dependency
    PlaywrightTimeoutError = RuntimeError
    sync_playwright = None


def collect_jobs_with_playwright(
    *,
    search_url: str,
    profile_dir: str,
    headless: bool,
    scroll_rounds: int,
    max_cards: int,
) -> tuple[list[JobPosting], str]:
    if sync_playwright is None:
        raise RuntimeError(
            "Playwright nao esta instalado. Rode 'pip install playwright' e "
            "'python -m playwright install chromium'."
        )
    if not search_url:
        raise ValueError("search_url nao foi definido no arquivo de configuracao.")

    profile_path = Path(profile_dir)
    profile_path.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            viewport={"width": 1440, "height": 1100},
        )
        try:
            page = context.new_page()
            page.goto(search_url, wait_until="domcontentloaded", timeout=90_000)
            _handle_login_pause(page, headless=headless)
            _dismiss_cookie_banner(page)
            _wait_for_job_results(page)
            _scroll_results(page, scroll_rounds=scroll_rounds)
            jobs = _extract_jobs(page, max_cards=max_cards)
            html_snapshot = page.content()
            return jobs, html_snapshot
        finally:
            context.close()


def _handle_login_pause(page, *, headless: bool) -> None:
    if headless:
        return

    current_url = page.url.lower()
    login_markers = ("linkedin.com/login", "linkedin.com/checkpoint", "/authwall")
    needs_login = any(marker in current_url for marker in login_markers)

    if needs_login:
        print("Login manual necessario no navegador aberto.")
        input("Depois de concluir o login e chegar na busca de vagas, pressione Enter para continuar...")
        return

    print("Se quiser ajustar filtros manualmente no navegador, faca isso agora.")
    input("Pressione Enter para iniciar a coleta das vagas visiveis...")


def _dismiss_cookie_banner(page) -> None:
    selectors = [
        'button[action-type="ACCEPT"]',
        'button[id*="accept"]',
        'button:has-text("Accept")',
        'button:has-text("Aceitar")',
    ]
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            if locator.is_visible(timeout=1_000):
                locator.click(timeout=1_000)
                return
        except Exception:
            continue


def _wait_for_job_results(page) -> None:
    selectors = [
        ".jobs-search-results-list",
        ".scaffold-layout__list",
        "ul.scaffold-layout__list-container",
        '[data-job-id]',
    ]
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=8_000)
            return
        except PlaywrightTimeoutError:
            continue
    raise RuntimeError("Nao foi possivel localizar a lista de vagas na pagina do LinkedIn.")


def _scroll_results(page, *, scroll_rounds: int) -> None:
    container_selectors = [
        ".jobs-search-results-list",
        ".scaffold-layout__list",
        "div.jobs-search-results-list",
    ]

    for selector in container_selectors:
        locator = page.locator(selector).first
        try:
            if not locator.is_visible(timeout=1_500):
                continue
            for _ in range(scroll_rounds):
                locator.evaluate("(node) => { node.scrollTop = node.scrollHeight; }")
                page.wait_for_timeout(1_200)
            return
        except Exception:
            continue

    for _ in range(scroll_rounds):
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1_200)


def _extract_jobs(page, *, max_cards: int) -> list[JobPosting]:
    cards = page.locator(
        "li:has(a[href*='/jobs/view/']), div:has(a[href*='/jobs/view/'])"
    )
    total = min(cards.count(), max_cards)
    jobs: list[JobPosting] = []

    for index in range(total):
        card = cards.nth(index)
        try:
            link = card.locator("a[href*='/jobs/view/']").first
            title = _safe_text(card, [
                ".job-card-list__title",
                ".artdeco-entity-lockup__title",
                "strong",
                "a[href*='/jobs/view/'] span[aria-hidden='true']",
                "a[href*='/jobs/view/']",
            ])
            company = _safe_text(card, [
                ".artdeco-entity-lockup__subtitle",
                ".job-card-container__company-name",
                ".job-card-container__primary-description",
            ])
            location = _safe_text(card, [
                ".job-card-container__metadata-wrapper",
                ".job-card-container__metadata-item",
                ".artdeco-entity-lockup__caption",
            ])
            url = link.get_attribute("href") or ""
            url = _normalize_job_url(url)

            if title and company:
                jobs.append(
                    JobPosting(
                        title=title,
                        company=company,
                        location=location,
                        url=url,
                        source_file=page.url,
                    )
                )
        except Exception:
            continue

    return _deduplicate(jobs)


def _safe_text(card, selectors: list[str]) -> str:
    for selector in selectors:
        try:
            text = card.locator(selector).first.inner_text(timeout=1_500).strip()
            if text:
                return " ".join(text.split())
        except Exception:
            continue
    return ""


def _normalize_job_url(url: str) -> str:
    if not url:
        return ""
    if url.startswith("/"):
        return f"https://www.linkedin.com{url.split('?', 1)[0]}"
    return url.split("?", 1)[0]


def _deduplicate(jobs: list[JobPosting]) -> list[JobPosting]:
    unique: dict[tuple[str, str, str], JobPosting] = {}
    for job in jobs:
        key = (job.title.lower(), job.company.lower(), job.url.lower())
        unique[key] = job
    return list(unique.values())
