import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT / "scraper"))
sys.path.append(str(ROOT / "analysis"))

from crawler import run as run_crawler
from eda import run_eda


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the IndiaMART data pipeline: collect/parse data, then generate EDA outputs."
    )
    parser.add_argument(
        "--html-file",
        help="Saved IndiaMART listing HTML file. Recommended for IndiaMART because direct crawling may be blocked.",
    )
    parser.add_argument("--url", default="saved_html", help="Source URL label for saved HTML or live URL scraping.")
    parser.add_argument("--category", default="industrial machinery", help="Category label for output rows.")
    parser.add_argument("--marketplace", default="indiamart", help="Marketplace label for output rows.")
    parser.add_argument("--live", action="store_true", help="Attempt live URL scraping instead of parsing saved HTML.")
    parser.add_argument("--ignore-robots", action="store_true", help="Disable robots.txt checks for controlled demos only.")
    parser.add_argument("--max-pages", type=int, default=1)
    parser.add_argument("--demo-data", action="store_true", help="Use bundled demo data, then run EDA.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.demo_data:
        records = run_crawler(use_demo_data=True)
    elif args.html_file:
        records = run_crawler(
            html_file=args.html_file,
            custom_url=args.url,
            custom_category=args.category,
            custom_marketplace=args.marketplace,
        )
    elif args.live:
        if args.url == "saved_html":
            raise SystemExit("Provide --url when using --live.")
        records = run_crawler(
            custom_url=args.url,
            custom_category=args.category,
            custom_marketplace=args.marketplace,
            max_pages=args.max_pages,
            respect_robots=not args.ignore_robots,
        )
    else:
        raise SystemExit(
            "For IndiaMART, use --html-file indiamart_page.html. "
            "Use --live --url ... only for permitted live crawling."
        )

    print(f"Data step completed: {len(records)} records saved.")
    summary = run_eda()
    print(f"EDA completed: {summary.get('row_count', 0)} rows analyzed.")
    print("Outputs: data/cleaned_products.csv, data/raw_products.json, analysis/outputs/")


if __name__ == "__main__":
    main()
