# Ten Chargeback Management — Zoho Creator App

## What this repo is
ForgeDS consumer project for Ten Group's chargeback management system.
Includes: Python ETL pipeline, Deluge workflows, HTML/JS dashboard, process documentation.

## Tech stack
- **Engine**: ForgeDS (pip-installable from HolgerRGevers/ForgeDS)
- **ETL**: Python >= 3.10, stdlib only (csv, json, zipfile, pathlib, datetime)
- **Dashboard**: HTML/JS + Chart.js (CDN, zero build step)
- **Target platform**: Zoho Creator / Deluge

## Repo structure
- `config/` — forgeds.yaml, deluge-manifest, email templates, seed data
- `src/etl/` — Python data pipeline (extract, parse, normalize, convert)
- `src/deluge/` — Deluge scripts (form-workflows, scheduled, custom-api)
- `src/dashboard/` — CFO/COO risk dashboard (static HTML/JS)
- `data/` — exchange_rates.json (committed), raw/ and clean/ (gitignored)
- `docs/` — Process documentation (current state, pain points, future state)
- `tests/` — ETL unit tests

## Key rules
- ETL pipeline must use stdlib only (no pandas, no requests)
- All currency amounts must be converted to USD for reporting
- Deluge scripts follow ForgeDS conventions (header comments, null guards, double quotes)
- 30-day dispute window is the critical business rule — all alerting based on this
- Exchange rates: USD base, rates are per-USD (divide amount by rate to get USD)

## Deluge conventions (from ForgeDS)
- Use double quotes for strings, not single quotes
- Always null-guard query results with ifnull()
- Never use banned functions (lpad, hoursBetween, etc.)
- Always include Added_User in insert blocks
- Use sendmail with all required parameters (to, from, subject, message)

## ETL pipeline usage
```bash
python -m src.etl.pipeline --zip "path/to/Chargeback Records (2).zip" --rates data/exchange_rates.json --output data/clean/
```
