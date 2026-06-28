# B2B Data Miner

A compact crawler + EDA pipeline for collecting product listings from B2B marketplaces such as IndiaMART and analyzing product, supplier, location, price, and data-quality patterns.

## Part A: Crawler

Targets are configured in `scraper/config.py` and focus on IndiaMART categories. Direct IndiaMART search crawling may be skipped by robots.txt, so the recommended IndiaMART workflow is parsing saved listing-page HTML.

- IndiaMART industrial machinery
- IndiaMART industrial electronics
- IndiaMART textile machinery

Run the crawler:

```powershell
python scraper/crawler.py --categories "industrial machinery" --max-pages 1
```

Useful options:

```powershell
python scraper/crawler.py --html-file indiamart_page.html --category "industrial machinery" --marketplace indiamart --url "https://dir.indiamart.com/search.mp?ss=industrial%20machinery"
python scraper/crawler.py --ignore-robots
python scraper/crawler.py --demo-data
```

The crawler is designed to be polite and maintainable:

- Uses a descriptive user agent.
- Checks `robots.txt` by default.
- Applies randomized delays between requests.
- Keeps category targets, paths, and rate limits in `scraper/config.py`.
- Parses marketplace cards through selector fallbacks instead of a single fragile CSS class.
- Writes raw JSON to `data/raw_products.json` and cleaned tabular data to `data/cleaned_products.csv`.


## Web App

Run the paste-a-link scraping page:

```powershell
python app.py
```

Open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

Use this page when you want someone to paste a marketplace/search URL manually, run the scraper from the browser, preview extracted rows, and save the same JSON/CSV files used by the EDA. If live marketplaces block crawling, use the saved HTML section: open the marketplace page manually, wait for products to appear, save or copy the page HTML, then upload/paste it into the app. You can also click Load demo dataset to populate realistic sample records for EDA and presentation.


## One-command pipeline

For IndiaMART, save the loaded listing page inside `html_pages/`, for example `html_pages/indiamart_industrial_machinery.html`, then run collection plus EDA together:

```powershell
python run_pipeline.py --html-file html_pages\indiamart_industrial_machinery.html --category "industrial machinery" --marketplace indiamart --url "https://dir.indiamart.com/search.mp?ss=industrial%20machinery"
```

This writes `data/cleaned_products.csv`, `data/raw_products.json`, and `analysis/outputs/` in one run.

## Part B: EDA

Run the repeatable EDA script:

```powershell
python analysis/eda.py
```

Outputs are written to `analysis/outputs/`:

- `summary.json`
- `category_counts.png`
- `price_distribution.png`
- `supplier_states.png`
- `top_keywords.png`

The notebook version lives at `analysis/eda.ipynb` for interactive review.

## Data Notes

This repository includes valid empty output files so the project structure is reproducible before the first crawl. In this sandbox, live IndiaMART access was unavailable, so execute the crawler from a Python environment with internet access to populate the dataset before running final EDA.







