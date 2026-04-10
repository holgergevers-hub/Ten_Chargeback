# Ten Chargeback Management

Zoho Creator application for managing chargebacks across multiple merchant platforms (Adyen, Ingenico, Stripe). Built with [ForgeDS](https://github.com/HolgerRGevers/ForgeDS).

## Overview

Ten Group's credit controllers manage chargebacks across 3 merchant platforms in different formats. This project provides:

- **ETL Pipeline** — Extracts, normalizes, and converts 9,438+ merchant statement files into a unified schema with USD amounts
- **Zoho Creator App** — Forms, workflows, and scheduled tasks for chargeback lifecycle management
- **CFO/COO Dashboard** — Interactive risk dashboard showing total exposure, trends, and regional breakdown
- **Process Documentation** — Current state mapping, pain point analysis, and future state model

## Quick Start

### 1. Run the ETL Pipeline

```bash
python -m src.etl.pipeline \
  --zip "path/to/Chargeback Records (2).zip" \
  --rates data/exchange_rates.json \
  --output data/clean/
```

This processes all merchant statement files and outputs:
- `chargeback_all.csv` — Clean, normalized records with USD conversion
- `dashboard_data.json` — Aggregated data for the dashboard
- `pipeline_summary.json` — Statistics and breakdown

### 2. View the Dashboard

Open `src/dashboard/index.html` in a browser (serve via local HTTP server for fetch to work):

```bash
cd src/dashboard
python -m http.server 8080
# Open http://localhost:8080
```

### 3. Deploy to Zoho Creator

```bash
pip install git+https://github.com/HolgerRGevers/ForgeDS.git
forgeds-lint src/deluge/
forgeds-validate data/clean/
forgeds-upload --config config/zoho-api.yaml --csv-dir data/clean/
```

## Data Pipeline

The ETL pipeline handles 3 different merchant platform formats:

| Platform | Format | Delimiter | Date Format | Amount Field |
|----------|--------|-----------|-------------|-------------|
| Adyen | CSV | Comma | Mixed (YYYY-MM-DD, MM/DD/YYYY) | Varies |
| Ingenico | JSON | N/A | DD-MM-YYYY | Varies |
| Stripe | Text | Pipe or Tab | YYYY-MM-DD | Varies |

Column names are inconsistent across merchant accounts within the same platform. The pipeline auto-detects delimiters, date formats, and field names.

## Key Results

- **Total Chargeback Exposure: $303,247.67 USD**
- 324 records across 3 platforms
- 322/324 records successfully converted to USD
- Currencies processed: GBP, EUR, USD, JPY

## Project Structure

```
config/               ForgeDS configuration, seed data, email templates
src/etl/              Python ETL pipeline (stdlib only, zero dependencies)
src/deluge/           Zoho Creator Deluge scripts
src/dashboard/        Interactive HTML/JS dashboard
data/                 Exchange rates and pipeline output
docs/                 Process documentation
```

## Requirements

- Python >= 3.10 (stdlib only, no external packages needed)
- ForgeDS (for linting and deployment)
