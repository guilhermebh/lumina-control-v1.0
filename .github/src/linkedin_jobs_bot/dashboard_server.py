from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from linkedin_jobs_bot.analytics import serialize_jobs, summarize_jobs
from linkedin_jobs_bot.models import JobPosting


class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory: str, jobs_path: Path, **kwargs):
        self.jobs_path = jobs_path
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/jobs":
            self._send_json(self._load_jobs_payload())
            return
        if self.path == "/api/summary":
            payload = self._load_jobs_payload()
            self._send_json(
                {
                    "jobs": payload["jobs"],
                    "summary": payload["summary"],
                    "meta": payload["meta"],
                }
            )
            return
        super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def _load_jobs_payload(self) -> dict:
        jobs = _load_jobs(self.jobs_path)
        return {
            "jobs": serialize_jobs(jobs),
            "summary": summarize_jobs(jobs),
            "meta": {
                "jobs_path": str(self.jobs_path),
                "exists": self.jobs_path.exists(),
            },
        }

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inicia o dashboard web do LinkedIn Jobs Bot.")
    parser.add_argument("--host", default="127.0.0.1", help="Host do servidor local.")
    parser.add_argument("--port", type=int, default=8765, help="Porta do servidor local.")
    parser.add_argument(
        "--jobs-file",
        default="output/jobs.json",
        help="Arquivo JSON gerado pelo bot com as vagas filtradas.",
    )
    args = parser.parse_args()

    root_dir = Path(__file__).resolve().parents[2]
    static_dir = root_dir / "webapp"
    jobs_path = root_dir / args.jobs_file

    def handler(*handler_args, **handler_kwargs):
        return DashboardRequestHandler(
            *handler_args,
            directory=str(static_dir),
            jobs_path=jobs_path,
            **handler_kwargs,
        )

    server = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"Dashboard disponivel em http://{args.host}:{args.port}")
    print(f"Arquivo de vagas: {jobs_path}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        server.server_close()
    return 0


def _load_jobs(path: Path) -> list[JobPosting]:
    if not path.exists():
        return []

    raw_data = json.loads(path.read_text(encoding="utf-8"))
    jobs: list[JobPosting] = []
    for item in raw_data:
        if not isinstance(item, dict):
            continue
        jobs.append(
            JobPosting(
                title=str(item.get("title", "")),
                company=str(item.get("company", "")),
                location=str(item.get("location", "")),
                url=str(item.get("url", "")),
                source_file=str(item.get("source_file", "")),
            )
        )
    return jobs
