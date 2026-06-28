"""
Automated EDA runner.

Use this file when you want a repeatable command-line analysis after scraping.
It reads data/cleaned_products.csv and writes machine-readable summaries plus
chart PNGs into analysis/outputs/.

For interactive explanation, presentation, and step-by-step exploration, use
analysis/eda.ipynb instead.
"""
import json
import re
from collections import Counter
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scraper"))

from config import CLEAN_CSV_PATH, EDA_OUTPUT_DIR


def top_keywords(names: pd.Series, limit: int = 20) -> dict[str, int]:
    stopwords = {
        "and",
        "for",
        "with",
        "the",
        "machine",
        "machines",
        "system",
        "plant",
    }
    words: list[str] = []
    for name in names.dropna():
        words.extend(
            word
            for word in re.findall(r"[a-zA-Z]{3,}", name.lower())
            if word not in stopwords
        )
    return dict(Counter(words).most_common(limit))


def save_bar(series: pd.Series, title: str, filename: str, xlabel: str = "") -> None:
    if series.empty:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    series.sort_values().plot(kind="barh", ax=ax, color="#2563eb")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(EDA_OUTPUT_DIR / filename, dpi=160)
    plt.close(fig)


def run_eda() -> dict:
    EDA_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not CLEAN_CSV_PATH.exists():
        raise FileNotFoundError(f"Missing dataset: {CLEAN_CSV_PATH}")

    df = pd.read_csv(CLEAN_CSV_PATH)
    if df.empty:
        print(
            "No scraped rows found in data/cleaned_products.csv. "
            "Run scraper/crawler.py first and confirm it saves records before interpreting EDA."
        )

    summary = {
        "data_status": "empty" if df.empty else "populated",
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "category_counts": df.get("category", pd.Series(dtype=str)).value_counts().to_dict(),
        "marketplace_counts": df.get("marketplace", pd.Series(dtype=str)).value_counts().to_dict(),
        "top_locations": df.get("location", pd.Series(dtype=str)).dropna().value_counts().head(10).to_dict(),
        "top_suppliers": df.get("supplier_name", pd.Series(dtype=str)).dropna().value_counts().head(10).to_dict(),
        "top_keywords": top_keywords(df.get("product_name", pd.Series(dtype=str))),
        "missing_values": df.isna().sum().astype(int).to_dict(),
    }

    price_column = "price_min" if "price_min" in df else "price_min_inr"
    if price_column in df:
        numeric_prices = pd.to_numeric(df[price_column], errors="coerce").dropna()
        summary[f"{price_column}_summary"] = numeric_prices.describe().fillna(0).to_dict()
        if not numeric_prices.empty:
            fig, ax = plt.subplots(figsize=(9, 5))
            numeric_prices.plot(kind="hist", bins=20, ax=ax, color="#16a34a", edgecolor="white")
            ax.set_title(f"Price Distribution ({price_column})")
            ax.set_xlabel("Minimum listed price")
            fig.tight_layout()
            fig.savefig(EDA_OUTPUT_DIR / "price_distribution.png", dpi=160)
            plt.close(fig)

    save_bar(
        df.get("category", pd.Series(dtype=str)).value_counts().head(10),
        "Products by Category",
        "category_counts.png",
        "Products",
    )
    save_bar(
        df.get("state", pd.Series(dtype=str)).dropna().value_counts().head(10),
        "Supplier States",
        "supplier_states.png",
        "Suppliers",
    )
    save_bar(
        pd.Series(summary["top_keywords"]),
        "Frequent Product Keywords",
        "top_keywords.png",
        "Mentions",
    )

    summary_path = EDA_OUTPUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = run_eda()
    print(json.dumps(result, indent=2))



