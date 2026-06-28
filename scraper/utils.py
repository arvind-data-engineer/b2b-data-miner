import csv
import json
import random
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests

from config import CSV_COLUMNS, REQUEST_TIMEOUT_SECONDS, USER_AGENT


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def polite_sleep(delay_range: tuple[int, int]) -> None:
    time.sleep(random.uniform(*delay_range))


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9",
        }
    )
    return session


def can_fetch(url: str, user_agent: str = USER_AGENT) -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    parser = RobotFileParser(robots_url)
    try:
        parser.read()
    except Exception:
        return True
    return parser.can_fetch(user_agent, url)


def fetch_html(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.text


def save_json(records: list[dict], path: Path) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def save_csv(records: Iterable[dict], path: Path) -> None:
    ensure_parent(path)
    rows = list(records)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
