import argparse
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from config import (
    CATEGORIES,
    CLEAN_CSV_PATH,
    MAX_PAGES_PER_CATEGORY,
    RATE_LIMIT_SECONDS,
    RAW_JSON_PATH,
    RESPECT_ROBOTS_TXT,
)
from parser import deduplicate, parse_marketplace_page
from sample_data import demo_records
from utils import build_session, can_fetch, fetch_html, polite_sleep, save_csv, save_json


def paginated_url(url: str, page_number: int) -> str:
    if page_number <= 1:
        return url
    parsed = urlparse(url)
    if parsed.netloc == "books.toscrape.com":
        return f"{parsed.scheme}://{parsed.netloc}/catalogue/page-{page_number}.html"
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["page"] = str(page_number)
    return urlunparse(parsed._replace(query=urlencode(query)))


def scrape_category(
    session,
    category: str,
    target: dict,
    *,
    max_pages: int,
    respect_robots: bool,
) -> list[dict]:
    records: list[dict] = []
    for page_number in range(1, max_pages + 1):
        url = paginated_url(target["url"], page_number)
        if respect_robots and not can_fetch(url):
            print(f"Skipped by robots.txt: {url}")
            continue

        print(f"Fetching {category} page {page_number}: {url}")
        try:
            html = fetch_html(session, url)
        except Exception as exc:
            print(f"Fetch failed for {url}: {exc}")
            continue

        page_records = parse_marketplace_page(
            html,
            category=category,
            marketplace=target["marketplace"],
            source_url=url,
        )
        print(f"Parsed {len(page_records)} product records")
        records.extend(page_records)
        polite_sleep(RATE_LIMIT_SECONDS)

    return deduplicate(records)


def run(
    selected_categories: list[str] | None = None,
    use_demo_data: bool = False,
    html_file: str | None = None,
    custom_url: str | None = None,
    custom_category: str = "custom",
    custom_marketplace: str = "custom",
    max_pages: int = MAX_PAGES_PER_CATEGORY,
    respect_robots: bool = RESPECT_ROBOTS_TXT,
) -> list[dict]:
    if use_demo_data:
        records = demo_records()
        save_json(records, RAW_JSON_PATH)
        save_csv(records, CLEAN_CSV_PATH)
        return records

    if html_file:
        html = open(html_file, "r", encoding="utf-8", errors="ignore").read()
        records = parse_marketplace_page(
            html,
            category=custom_category,
            marketplace=custom_marketplace,
            source_url=custom_url or html_file,
        )
        records = deduplicate(records)
        save_json(records, RAW_JSON_PATH)
        save_csv(records, CLEAN_CSV_PATH)
        if not records:
            print(
                "Warning: saved HTML parsed 0 records. Save the full loaded listing page "
                "after product cards are visible, or update parser selectors."
            )
        return records

    session = build_session()
    all_records: list[dict] = []

    if custom_url:
        all_records.extend(
            scrape_category(
                session,
                custom_category,
                {"marketplace": custom_marketplace, "url": custom_url},
                max_pages=max_pages,
                respect_robots=respect_robots,
            )
        )
    else:
        selected = selected_categories or list(CATEGORIES)
        for category in selected:
            target = CATEGORIES.get(category)
            if not target:
                print(f"Unknown category skipped: {category}")
                continue
            all_records.extend(
                scrape_category(
                    session,
                    category,
                    target,
                    max_pages=max_pages,
                    respect_robots=respect_robots,
                )
            )

    all_records = deduplicate(all_records)
    save_json(all_records, RAW_JSON_PATH)
    save_csv(all_records, CLEAN_CSV_PATH)
    if not all_records:
        print(
            "Warning: crawler saved 0 records. Check fetch errors above, robots.txt skips, "
            "or marketplace blocking/HTML structure changes."
        )
    return all_records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Polite B2B marketplace product crawler")
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES_PER_CATEGORY)
    parser.add_argument("--categories", nargs="*", choices=sorted(CATEGORIES))
    parser.add_argument("--url", help="Scrape one pasted search/listing URL or label saved HTML source")
    parser.add_argument("--html-file", help="Parse a saved IndiaMART/listing HTML file instead of fetching the URL")
    parser.add_argument("--category", default="custom", help="Category label for --url")
    parser.add_argument("--marketplace", default="custom", help="Marketplace label for --url")
    parser.add_argument("--ignore-robots", action="store_true")
    parser.add_argument("--demo-data", action="store_true", help="Save bundled demo records for EDA when live sites block crawling")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    products = run(
        selected_categories=args.categories,
        use_demo_data=args.demo_data,
        html_file=args.html_file,
        custom_url=args.url,
        custom_category=args.category,
        custom_marketplace=args.marketplace,
        max_pages=args.max_pages,
        respect_robots=not args.ignore_robots,
    )
    print(f"Scraping completed. Saved {len(products)} records.")





