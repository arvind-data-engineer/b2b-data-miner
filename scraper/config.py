from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = BASE_DIR / "analysis"
EDA_OUTPUT_DIR = ANALYSIS_DIR / "outputs"

RAW_JSON_PATH = DATA_DIR / "raw_products.json"
CLEAN_CSV_PATH = DATA_DIR / "cleaned_products.csv"

USER_AGENT = (
    "B2BDataMiner/1.0 (+academic portfolio crawler; "
    "polite rate-limited requests)"
)

REQUEST_TIMEOUT_SECONDS = 30
RATE_LIMIT_SECONDS = (4, 9)
MAX_PAGES_PER_CATEGORY = 2
RESPECT_ROBOTS_TXT = True

CATEGORIES = {
    "industrial machinery": {
        "marketplace": "indiamart",
        "url": "https://dir.indiamart.com/search.mp?ss=industrial%20machinery",
    },
    "electronics": {
        "marketplace": "indiamart",
        "url": "https://dir.indiamart.com/search.mp?ss=industrial%20electronics",
    },
    "textiles": {
        "marketplace": "indiamart",
        "url": "https://dir.indiamart.com/search.mp?ss=textile%20machinery",
    },
}

CSV_COLUMNS = [
    "category",
    "marketplace",
    "product_name",
    "price",
    "currency",
    "price_min",
    "price_max",
    "price_min_inr",
    "price_max_inr",
    "supplier_name",
    "location",
    "city",
    "state",
    "product_url",
    "source_url",
    "scraped_date",
]
