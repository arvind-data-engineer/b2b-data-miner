import re
from datetime import datetime
from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


CARD_SELECTORS = [
    "[class*='lst_cl']",
    "[class*='prd-list']",
    "[class*='product-list']",
    "article.product_pod",
    "[class*='fy23-search-card']",
    "[class*='search-card']",
    "[class*='organic-gallery']",
    "[class*='product-card']",
    "[data-testid*='product']",
    "[class*='product']",
    "[class*='prd']",
    "[class*='card']",
    "[class*='listing']",
    "li",
]

NAME_SELECTORS = [
    "[class*='prd-name']",
    "[class*='product-name']",
    "[class*='producttitle']",
    "[class*='search-card-e-title']",
    "[class*='elements-title']",
    "[class*='product-title']",
    "[class*='title']",
    "h2",
    "h3",
    "a[title]",
    "a",
]

PRICE_SELECTORS = [
    "[class*='prc']",
    "[class*='price']",
    "[class*='search-card-e-price-main']",
    "[class*='price-main']",
    "[class*='rs']",
    "[class*='amount']",
]

SUPPLIER_SELECTORS = [
    "[class*='cmp']",
    "[class*='companyname']",
    "[class*='supplier']",
    "[class*='search-card-e-company']",
    "[class*='company']",
    "[class*='seller']",
    "[class*='store']",
]

LOCATION_SELECTORS = [
    "[class*='loc']",
    "[class*='location']",
    "[class*='search-card-e-country']",
    "[class*='country']",
    "[class*='city']",
    "[class*='addr']",
    "[class*='state']",
]

INDIAN_STATES = {
    "andhra pradesh", "delhi", "gujarat", "haryana", "karnataka",
    "maharashtra", "punjab", "rajasthan", "tamil nadu", "telangana",
    "uttar pradesh", "west bengal",
}


def clean_text(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.sub(r"\s+", " ", value).strip(" \t\r\n-|")
    return cleaned or None


def first_text(card: Tag, selectors: Iterable[str]) -> str | None:
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True) or element.get("title"))
            if text:
                return text
    return None


def product_link(card: Tag, base_url: str) -> str | None:
    anchor = card.select_one("a[href]")
    if not anchor:
        return None
    href = anchor.get("href")
    if not href or href.startswith(("javascript:", "#")):
        return None
    return urljoin(base_url, href)


def detect_currency(price: str | None) -> str | None:
    if not price:
        return None
    lowered = price.lower()
    if "$" in price or "usd" in lowered or "us $" in lowered:
        return "USD"
    if "£" in price or "gbp" in lowered:
        return "GBP"
    if "₹" in price or "rs" in lowered or "inr" in lowered:
        return "INR"
    return None


def parse_price_range(price: str | None) -> tuple[float | None, float | None]:
    if not price:
        return None, None
    normalized = price.replace(",", "")
    values = [
        float(match)
        for match in re.findall(
            r"(?:rs\.?|inr|usd|gbp|us\s*\$|\$|£|₹)?\s*(\d+(?:\.\d+)?)",
            normalized,
            re.I,
        )
    ]
    if not values:
        return None, None
    if any(token in normalized.lower() for token in ["lakh", "lac"]):
        values = [value * 100000 for value in values]
    elif "crore" in normalized.lower():
        values = [value * 10000000 for value in values]
    return min(values), max(values)


def split_location(location: str | None) -> tuple[str | None, str | None]:
    if not location:
        return None, None
    parts = [part.strip() for part in re.split(r"[,|]", location) if part.strip()]
    state = None
    for part in reversed(parts):
        if part.lower() in INDIAN_STATES:
            state = part
            break
    city = parts[0] if parts else None
    return city, state


def parse_books_to_scrape(soup: BeautifulSoup, *, category: str, marketplace: str, source_url: str) -> list[dict]:
    records: list[dict] = []
    scraped_date = datetime.now().strftime("%Y-%m-%d")
    for card in soup.select("article.product_pod"):
        title_node = card.select_one("h3 a")
        price_node = card.select_one(".price_color")
        availability_node = card.select_one(".availability")
        title = clean_text(title_node.get("title") if title_node else None)
        price = clean_text(price_node.get_text(" ", strip=True) if price_node else None)
        availability = clean_text(availability_node.get_text(" ", strip=True) if availability_node else None)
        if not title:
            continue
        price_min, price_max = parse_price_range(price)
        currency = detect_currency(price)
        records.append(build_record(category, marketplace, title, price, currency, price_min, price_max, "Books to Scrape", availability, card, source_url, scraped_date))
    return records


def build_record(category, marketplace, product_name, price, currency, price_min, price_max, supplier_name, location, card, source_url, scraped_date):
    city, state = split_location(location)
    return {
        "category": category,
        "marketplace": marketplace,
        "product_name": product_name,
        "price": price,
        "currency": currency,
        "price_min": price_min,
        "price_max": price_max,
        "price_min_inr": price_min if currency == "INR" else None,
        "price_max_inr": price_max if currency == "INR" else None,
        "supplier_name": supplier_name,
        "location": location,
        "city": city,
        "state": state,
        "product_url": product_link(card, source_url),
        "source_url": source_url,
        "scraped_date": scraped_date,
    }


def candidate_cards(soup: BeautifulSoup) -> list[Tag]:
    cards: list[Tag] = []
    seen: set[int] = set()
    markers = [
        "₹", "rs", "inr", "$", "usd", "£", "gbp", "min. order",
        "supplier", "seller", "company", "verified", "alibaba", "in stock",
        "add to basket", "get latest price", "indiamart", "contact supplier",
    ]
    for selector in CARD_SELECTORS:
        for card in soup.select(selector):
            identity = id(card)
            if identity in seen:
                continue
            text = card.get_text(" ", strip=True).lower()
            if len(text) < 20:
                continue
            if any(marker in text for marker in markers):
                seen.add(identity)
                cards.append(card)
    return cards



def parse_indiamart_static_preview(
    soup: BeautifulSoup,
    *,
    category: str,
    marketplace: str,
    source_url: str,
) -> list[dict]:
    records: list[dict] = []
    scraped_date = datetime.now().strftime("%Y-%m-%d")
    for card in soup.select("section.staticListingCard"):
        title = first_text(card, ["h2", "h3", "a[title]", "a"])
        supplier_box = card.select_one(".staticSupplierBox")
        location = clean_text(supplier_box.select_one("strong").get_text(" ", strip=True)) if supplier_box and supplier_box.select_one("strong") else None
        supplier_name = clean_text(supplier_box.get_text(" ", strip=True)) if supplier_box else None
        if supplier_name and "contact supplier" in supplier_name.lower():
            supplier_name = clean_text(re.sub(r"contact supplier", "", supplier_name, flags=re.I))
        if not title:
            continue
        records.append(
            build_record(
                category,
                marketplace,
                title,
                None,
                None,
                None,
                None,
                supplier_name or "IndiaMART supplier",
                location,
                card,
                source_url,
                scraped_date,
            )
        )
    return records

def parse_marketplace_page(html: str, *, category: str, marketplace: str, source_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    if "staticSearchPreview" in html and '"searchResponse":null' in html:
        print(
            "Warning: this IndiaMART HTML contains only the static preview shell, "
            "not real loaded product results. Save/copy the rendered DOM after products load."
        )
        return []

    if soup.select_one("section.staticListingCard"):
        return deduplicate(
            parse_indiamart_static_preview(
                soup,
                category=category,
                marketplace=marketplace,
                source_url=source_url,
            )
        )

    if marketplace == "books_to_scrape" or soup.select_one("article.product_pod"):
        return deduplicate(parse_books_to_scrape(soup, category=category, marketplace=marketplace, source_url=source_url))

    records: list[dict] = []
    scraped_date = datetime.now().strftime("%Y-%m-%d")
    for card in candidate_cards(soup):
        product_name = first_text(card, NAME_SELECTORS)
        price = first_text(card, PRICE_SELECTORS)
        supplier_name = first_text(card, SUPPLIER_SELECTORS)
        location = first_text(card, LOCATION_SELECTORS)
        if not product_name:
            continue
        price_min, price_max = parse_price_range(price)
        currency = detect_currency(price)
        records.append(build_record(category, marketplace, product_name, price, currency, price_min, price_max, supplier_name, location, card, source_url, scraped_date))
    return deduplicate(records)


def deduplicate(records: list[dict]) -> list[dict]:
    unique: list[dict] = []
    seen: set[tuple[str | None, str | None]] = set()
    for record in records:
        key = (record.get("product_name"), record.get("supplier_name"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


