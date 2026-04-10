# Ten Chargeback Management

Zoho Creator application for managing chargebacks across multiple merchant platforms (Adyen, Ingenico, Stripe). Built with [ForgeDS](https://github.com/HolgerRGevers/ForgeDS).

<div align="center">

[![View Dashboard](https://img.shields.io/badge/View_Dashboard-0f172a?style=for-the-badge&logo=chartdotjs&logoColor=3b82f6&labelColor=0f172a)](https://holgergevers-hub.github.io/Ten_Chargeback/src/dashboard/index.html)

**$303,247.67 USD** total exposure | **324** disputes | **3** platforms

[![Download App Definition (.ds)](https://img.shields.io/badge/Download_.ds_File-22c55e?style=for-the-badge&logo=zoho&logoColor=white&labelColor=166534)](ten_chargeback_management.ds)

</div>

---

## Deploy to Zoho Creator

### Option A: Import the .ds file (recommended)

1. Download [**ten_chargeback_management.ds**](ten_chargeback_management.ds) — contains all 9 forms, fields, workflows, and schedules in one file
2. In Zoho Creator: **Settings > Import Application > Upload .ds file**
3. Import the seed data:

| Upload this file | Into this form | Records |
|-----------------|---------------|---------|
| [`regional_config.json`](config/seed-data/regional_config.json) | `regional_config` | 38 merchant accounts |
| [`dispute_reason_codes.json`](config/seed-data/dispute_reason_codes.json) | `dispute_reason_codes` | 13 reason codes |
| [`merchant_platforms.json`](config/seed-data/merchant_platforms.json) | `merchant_platforms` | 3 platforms |
| [`currency_config.json`](config/seed-data/currency_config.json) | `currency_config` | 11 currencies |

4. Run the ETL pipeline and import chargebacks:

```bash
python -m src.etl.pipeline \
  --zip "path/to/Chargeback Records (2).zip" \
  --rates data/exchange_rates.json \
  --output data/clean/
```

5. Import `data/clean/chargeback_all.csv` into the `chargeback_incidents` form

> **How to import data:** Open the form > **Import Data** (top-right) > upload CSV/JSON > map columns > Import.

### Option B: Build manually

See [FORM_SCHEMA.md](src/deluge/setup/FORM_SCHEMA.md) for field definitions, then paste scripts from [`src/deluge/`](src/deluge/) into workflows.

### What's in the .ds file

| Component | Count | Details |
|-----------|-------|---------|
| Forms | 9 | chargeback_incidents, dispute_submissions, audit_trail, regional_config, dispute_reason_codes, merchant_platforms, currency_config, lm_followups, merchant_responses, file_uploads |
| Reports | 8 | All Chargebacks, Open Chargebacks, Expiring Soon, All Disputes, Audit Log, + 3 config views |
| Workflows | 2 | Auto-assign LM on chargeback, update status on dispute |
| Schedules | 4 | 25-day alerts (06:00), file processing (02:00), currency conversion (03:00), data cleansing (04:00) |

---

## Overview

Ten Group's credit controllers manage chargebacks across 3 merchant platforms in different formats. This project provides:

- **ETL Pipeline** — Extracts, normalizes, and converts 9,438+ merchant statement files into a unified schema with USD amounts
- **Zoho Creator App** — Forms, workflows, and scheduled tasks for chargeback lifecycle management
- **CFO/COO Dashboard** — Interactive risk dashboard showing total exposure, trends, and regional breakdown
- **Process Documentation** — Current state mapping, pain point analysis, and future state model

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
