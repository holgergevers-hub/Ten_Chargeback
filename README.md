# Ten Chargeback Management

Zoho Creator application for managing chargebacks across multiple merchant platforms (Adyen, Ingenico, Stripe). Built with [ForgeDS](https://github.com/HolgerRGevers/ForgeDS).

<div align="center">

[![View Dashboard](https://img.shields.io/badge/View_Dashboard-0f172a?style=for-the-badge&logo=chartdotjs&logoColor=3b82f6&labelColor=0f172a)](https://holgergevers-hub.github.io/Ten_Chargeback/src/dashboard/index.html)

**$303,247.67 USD** total exposure | **324** disputes | **3** platforms

</div>

</div>

---

## Zoho Creator Setup

### Step 1: Create the app and forms

Create a new Zoho Creator app, then add these 6 forms. See [FORM_SCHEMA.md](src/deluge/setup/FORM_SCHEMA.md) for all field names and types.

| # | Form | Purpose |
|---|------|---------|
| 1 | `regional_config` | Merchant account lookup (region, currency, LM assignment) |
| 2 | `dispute_reason_codes` | Visa/MC/Amex reason code reference |
| 3 | `chargeback_incidents` | Main chargeback records |
| 4 | `dispute_submissions` | Evidence submissions linked to incidents |
| 5 | `audit_trail` | System-wide activity log |
| 6 | `file_uploads` | Merchant file import tracking |

### Step 2: Upload data

Run the ETL pipeline, then import the CSVs into your forms:

```bash
python -m src.etl.pipeline \
  --zip "path/to/Chargeback Records (2).zip" \
  --rates data/exchange_rates.json \
  --output data/clean/
```

| Upload this file | Into this form | Notes |
|-----------------|---------------|-------|
| `data/clean/chargeback_all.csv` | `chargeback_incidents` | Main records (324 rows) |
| `config/seed-data/regional_config.json` | `regional_config` | 38 merchant accounts — update LM names/emails after import |
| `config/seed-data/dispute_reason_codes.json` | `dispute_reason_codes` | 13 Visa/MC/Amex reason codes |

> **How to import:** Open the form in Zoho Creator > click **Import Data** (top-right) > upload the CSV/JSON > map columns > Import.

### Step 3: Add workflows

Once the forms and data are in place, paste each Deluge script into its location. No edits needed.

**Form Workflows**

| Script | Paste Location | Trigger |
|--------|---------------|---------|
| [chargeback_incident.on_success.dg](src/deluge/form-workflows/chargeback_incident.on_success.dg) | Chargeback_Incidents > Workflow > On Success | After form submit |
| [dispute_submission.on_success.dg](src/deluge/form-workflows/dispute_submission.on_success.dg) | Dispute_Submissions > Workflow > On Success | After form submit |

**Scheduled Tasks** — Create under Workflow > Schedules

| Script | Schedule Name | Run At |
|--------|--------------|--------|
| [daily_file_processing.dg](src/deluge/scheduled/daily_file_processing.dg) | Daily_File_Processing | Daily 02:00 |
| [currency_conversion_batch.dg](src/deluge/scheduled/currency_conversion_batch.dg) | Currency_Conversion_Batch | Daily 03:00 |
| [data_cleansing_scheduled.dg](src/deluge/scheduled/data_cleansing_scheduled.dg) | Data_Cleansing | Daily 04:00 |
| [auto_alert_25_days.dg](src/deluge/scheduled/auto_alert_25_days.dg) | Auto_Alert_25_Days | Daily 06:00 |

**Custom APIs** — Create under Microservices > Custom API *(when ready)*

| Script | API Name |
|--------|----------|
| [get_dashboard_summary.dg](src/deluge/custom-api/get_dashboard_summary.dg) | Get_Dashboard_Summary |
| [get_aging_report.dg](src/deluge/custom-api/get_aging_report.dg) | Get_Aging_Report |

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
