from pathlib import Path
from urllib.parse import urlparse
import re
import sys

from flask import Flask, render_template, request

ROOT = Path(__file__).resolve().parent
HTML_DIR = ROOT / "html_pages"
sys.path.append(str(ROOT / "scraper"))

from config import CLEAN_CSV_PATH, RATE_LIMIT_SECONDS, RAW_JSON_PATH
from crawler import paginated_url
from parser import deduplicate, parse_marketplace_page
from sample_data import demo_records
from utils import build_session, can_fetch, fetch_html, polite_sleep, save_csv, save_json


app = Flask(__name__)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "page"


def saved_html_path(marketplace: str, category: str) -> Path:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    return HTML_DIR / f"{slugify(marketplace)}_{slugify(category)}.html"


def valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def fetched_html_path(marketplace: str, category: str, page_number: int) -> Path:
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    return HTML_DIR / f"fetched_{slugify(marketplace)}_{slugify(category)}_page_{page_number}.html"


def scrape_url_with_feedback(
    *,
    url: str,
    category: str,
    marketplace: str,
    max_pages: int,
    respect_robots: bool,
) -> tuple[list[dict], list[str], Path | None]:
    session = build_session()
    records: list[dict] = []
    messages: list[str] = []
    last_saved_path = None

    for page_number in range(1, max_pages + 1):
        page_url = paginated_url(url, page_number)
        if respect_robots and not can_fetch(page_url):
            messages.append(f"Page {page_number} was skipped because robots.txt does not allow automated crawling.")
            continue

        try:
            html = fetch_html(session, page_url)
        except Exception as exc:
            messages.append(f"Page {page_number} could not be fetched: {exc}")
            continue

        html_path = fetched_html_path(marketplace, category, page_number)
        html_path.write_text(html, encoding="utf-8", errors="ignore")
        last_saved_path = html_path

        page_records = parse_marketplace_page(
            html,
            category=category,
            marketplace=marketplace,
            source_url=page_url,
        )
        records.extend(page_records)

        if not page_records:
            messages.append(
                f"Page {page_number} was fetched and saved, but the parser found 0 product rows. "
                "The page may render products with JavaScript or use selectors this parser does not know yet."
            )

        if page_number < max_pages:
            polite_sleep(RATE_LIMIT_SECONDS)

    return deduplicate(records), messages, last_saved_path


def render_index(records=None, error=None, form=None, saved_path=None, messages=None):
    return render_template(
        "index.html",
        records=records or [],
        error=error,
        messages=messages or [],
        form=form
        or {
            "url": "",
            "category": "industrial machinery",
            "marketplace": "indiamart",
            "max_pages": "1",
            "respect_robots": "on",
            "html_source_url": "",
        },
        csv_path=CLEAN_CSV_PATH,
        json_path=RAW_JSON_PATH,
        saved_path=saved_path,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    records = []
    error = None
    saved_path = None
    messages = []
    form = {
        "url": "",
        "category": "industrial machinery",
        "marketplace": "indiamart",
        "max_pages": "1",
        "respect_robots": "on",
        "html_source_url": "",
    }

    if request.method == "POST":
        form.update(request.form.to_dict())
        if "load_demo" in request.form:
            records = demo_records()
            save_json(records, RAW_JSON_PATH)
            save_csv(records, CLEAN_CSV_PATH)
            return render_index(records=records, form=form)

        if "parse_html" in request.form:
            category = form.get("category", "industrial machinery").strip() or "industrial machinery"
            marketplace = form.get("marketplace", "indiamart").strip() or "indiamart"
            source_url = form.get("html_source_url", "saved_html").strip() or "saved_html"
            html_text = form.get("html_text", "")
            upload = request.files.get("html_file")
            if upload and upload.filename:
                html_text = upload.read().decode("utf-8", errors="ignore")

            if not html_text.strip():
                error = "Upload an HTML file or paste page HTML first."
            else:
                html_path = saved_html_path(marketplace, category)
                html_path.write_text(html_text, encoding="utf-8", errors="ignore")
                saved_path = html_path.relative_to(ROOT)
                records = parse_marketplace_page(
                    html_text,
                    category=category,
                    marketplace=marketplace,
                    source_url=source_url,
                )
                records = deduplicate(records)
                save_json(records, RAW_JSON_PATH)
                save_csv(records, CLEAN_CSV_PATH)
                if not records:
                    error = (
                        "HTML was saved, but no product rows matched the parser. "
                        "Save the full page after products are visible, or update parser selectors for that page."
                    )
            return render_index(records=records, error=error, form=form, saved_path=saved_path)

        url = form["url"].strip()
        category = form["category"].strip() or "industrial machinery"
        marketplace = form["marketplace"].strip() or "indiamart"

        try:
            max_pages = max(1, min(int(form.get("max_pages", "1")), 5))
        except ValueError:
            max_pages = 1

        respect_robots = form.get("respect_robots") == "on"

        if not valid_url(url):
            error = "Paste a valid http or https URL."
        elif respect_robots and not can_fetch(url):
            error = (
                "robots.txt does not allow this URL for automated crawling. "
                "Use the saved HTML section for IndiaMART pages."
            )
        else:
            records, messages, fetched_path = scrape_url_with_feedback(
                url=url,
                category=category,
                marketplace=marketplace,
                max_pages=max_pages,
                respect_robots=respect_robots,
            )
            saved_path = fetched_path.relative_to(ROOT) if fetched_path else None
            save_json(records, RAW_JSON_PATH)
            save_csv(records, CLEAN_CSV_PATH)
            if not records:
                error = (
                    "The page was fetched, but no product rows matched the parser. "
                    "For JavaScript-heavy marketplaces like IndiaMART, open the page manually, wait for products, "
                    "then use the saved HTML section."
                )

    return render_index(records=records, error=error, form=form, saved_path=saved_path, messages=messages)


if __name__ == "__main__":
    app.run(debug=True)
