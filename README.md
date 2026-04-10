# Ten Chargeback Management

Zoho Creator application for managing chargebacks across multiple merchant platforms (Adyen, Ingenico, Stripe). Built with [ForgeDS](https://github.com/HolgerRGevers/ForgeDS).

<div align="center">

[![View Dashboard](https://img.shields.io/badge/View_Dashboard-0f172a?style=for-the-badge&logo=chartdotjs&logoColor=3b82f6&labelColor=0f172a)](https://holgergevers-hub.github.io/Ten_Chargeback/src/dashboard/index.html)

**$303,247.67 USD** total exposure | **324** disputes | **3** platforms

</div>

[![Download Deluge Scripts](https://img.shields.io/badge/Download_Deluge_Scripts-1e293b?style=for-the-badge&logo=zoho&logoColor=22c55e&labelColor=1e293b)](https://github.com/holgergevers-hub/Ten_Chargeback/tree/main/src/deluge)

</div>

---

## Zoho Creator Import Guide

Copy each script into the corresponding location in Zoho Creator. No edits needed — scripts are ready to paste.

### Form Workflows

| Script | Paste Location | Trigger |
|--------|---------------|---------|
| [chargeback_incident.on_success.dg](src/deluge/form-workflows/chargeback_incident.on_success.dg) | Chargeback_Incidents form > Workflow > On Success | After form submit |
| [dispute_submission.on_success.dg](src/deluge/form-workflows/dispute_submission.on_success.dg) | Dispute_Submissions form > Workflow > On Success | After form submit |

### Scheduled Tasks

| Script | Paste Location | Schedule |
|--------|---------------|----------|
| [auto_alert_25_days.dg](src/deluge/scheduled/auto_alert_25_days.dg) | Workflow > Schedules > Auto_Alert_25_Days | Daily 06:00 |
| [daily_file_processing.dg](src/deluge/scheduled/daily_file_processing.dg) | Workflow > Schedules > Daily_File_Processing | Daily 02:00 |
| [currency_conversion_batch.dg](src/deluge/scheduled/currency_conversion_batch.dg) | Workflow > Schedules > Currency_Conversion_Batch | Daily 03:00 |
| [data_cleansing_scheduled.dg](src/deluge/scheduled/data_cleansing_scheduled.dg) | Workflow > Schedules > Data_Cleansing | Daily 04:00 |

### Custom APIs

| Script | Paste Location | Trigger |
|--------|---------------|---------|
| [get_dashboard_summary.dg](src/deluge/custom-api/get_dashboard_summary.dg) | Microservices > Custom API > Get_Dashboard_Summary | REST/widget call |
| [get_aging_report.dg](src/deluge/custom-api/get_aging_report.dg) | Microservices > Custom API > Get_Aging_Report | REST/widget call |

> **Setup order:** Create the forms (`chargeback_incidents`, `dispute_submissions`, `audit_trail`, `regional_config`, `file_uploads`) first, then add the workflows and schedules.

---

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

[**Open the Dashboard**](https://holgergevers-hub.github.io/Ten_Chargeback/src/dashboard/index.html)

Or serve locally (required if dashboard fetches external data):

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
