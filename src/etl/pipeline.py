"""ETL pipeline orchestrator for Ten Chargeback data.

Usage:
    python -m src.etl.pipeline --zip "path/to/Chargeback Records (2).zip" --rates data/exchange_rates.json --output data/clean/
"""

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

from .extract import extract_zip, get_exchange_rates_path
from .parse_adyen import parse_all as parse_adyen
from .parse_ingenico import parse_all as parse_ingenico
from .parse_stripe import parse_all as parse_stripe
from .normalize import (
    UNIFIED_FIELDS,
    normalize_adyen,
    normalize_ingenico,
    normalize_stripe,
)
from .currency_converter import CurrencyConverter, convert_records


def run_pipeline(zip_path: str, rates_path: str, output_dir: str) -> dict:
    """Run the full ETL pipeline.

    Returns a summary dict with counts and statistics.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Extract ---
    print("[1/5] Extracting zip archive...")
    raw_dir = output_dir.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest = extract_zip(zip_path, str(raw_dir))

    # Use exchange rates from zip if not provided separately
    if not Path(rates_path).exists():
        extracted_rates = get_exchange_rates_path(zip_path, str(raw_dir))
        if extracted_rates.exists():
            rates_path = str(extracted_rates)

    for platform, info in manifest.items():
        total_files = sum(len(files) for files in info["merchants"].values())
        print(f"  {platform}: {len(info['merchants'])} merchants, {total_files} files")

    # --- Step 2: Parse ---
    print("[2/5] Parsing platform files...")
    parsers = {
        "Adyen": parse_adyen,
        "Ingenico": parse_ingenico,
        "Stripe": parse_stripe,
    }

    raw_records = {}
    for platform, info in manifest.items():
        parser = parsers.get(platform)
        if not parser:
            continue
        platform_records = []
        for merchant, files in info["merchants"].items():
            records = parser(files)
            platform_records.extend([(merchant, r) for r in records])
        raw_records[platform] = platform_records
        print(f"  {platform}: {len(platform_records)} records parsed")

    # --- Step 3: Normalize ---
    print("[3/5] Normalizing records to unified schema...")
    normalizers = {
        "Adyen": normalize_adyen,
        "Ingenico": normalize_ingenico,
        "Stripe": normalize_stripe,
    }

    all_normalized = []
    for platform, merchant_records in raw_records.items():
        normalizer = normalizers[platform]
        for merchant, row in merchant_records:
            normalized = normalizer(row, merchant)
            all_normalized.append(normalized)

    print(f"  Total normalized records: {len(all_normalized)}")

    # --- Step 4: Currency conversion ---
    print("[4/5] Converting currencies to USD...")
    converter = CurrencyConverter(rates_path)
    print(f"  Supported currencies: {sorted(converter.supported_currencies)}")

    converted, needs_review = convert_records(all_normalized, converter)
    print(f"  Converted: {len(converted)}, Needs review: {len(needs_review)}")

    # --- Step 5: Output ---
    print("[5/5] Writing output files...")

    # Write main CSV (all records, including needs_review with 0 USD)
    all_records = converted + needs_review
    csv_fields = [f for f in UNIFIED_FIELDS if not f.startswith("_")]

    csv_path = output_dir / "chargeback_all.csv"
    _write_csv(csv_path, all_records, csv_fields)
    print(f"  {csv_path}: {len(all_records)} records")

    # Write needs-review CSV
    if needs_review:
        review_fields = csv_fields + ["_conversion_status"]
        review_path = output_dir / "chargeback_needs_review.csv"
        _write_csv(review_path, needs_review, review_fields)
        print(f"  {review_path}: {len(needs_review)} records")

    # Write pipeline summary
    summary = _build_summary(all_records, converted, needs_review)
    summary_path = output_dir / "pipeline_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"  {summary_path}: summary statistics")

    # Write dashboard data
    dashboard_data = _build_dashboard_data(all_records)
    dashboard_path = output_dir / "dashboard_data.json"
    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2)
    print(f"  {dashboard_path}: dashboard aggregations")

    print(f"\nPipeline complete. Total chargeback amount: ${summary['total_usd']:,.2f} USD")
    return summary


def _write_csv(path: Path, records: list[dict], fields: list[str]):
    """Write records to a CSV file."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def _build_summary(all_records, converted, needs_review) -> dict:
    """Build pipeline summary statistics."""
    total_usd = sum(r["amount_usd"] for r in all_records)
    by_platform = Counter(r["platform"] for r in all_records)
    by_record_type = Counter(r["record_type"] for r in all_records)
    by_currency = Counter(r["currency_original"] for r in all_records)
    by_merchant = Counter(r["merchant_account"] for r in all_records)

    # Amount by platform
    usd_by_platform = {}
    for r in all_records:
        p = r["platform"]
        usd_by_platform[p] = usd_by_platform.get(p, 0) + r["amount_usd"]

    # Amount by merchant
    usd_by_merchant = {}
    for r in all_records:
        m = r["merchant_account"]
        usd_by_merchant[m] = usd_by_merchant.get(m, 0) + r["amount_usd"]

    return {
        "total_records": len(all_records),
        "total_converted": len(converted),
        "total_needs_review": len(needs_review),
        "total_usd": round(total_usd, 2),
        "by_platform": dict(by_platform),
        "by_record_type": dict(by_record_type),
        "by_currency": dict(by_currency),
        "by_merchant": dict(by_merchant),
        "usd_by_platform": {k: round(v, 2) for k, v in usd_by_platform.items()},
        "usd_by_merchant": {k: round(v, 2) for k, v in sorted(usd_by_merchant.items(), key=lambda x: -x[1])},
    }


def _build_dashboard_data(records: list[dict]) -> dict:
    """Build aggregated data for the dashboard."""
    total_usd = sum(r["amount_usd"] for r in records)
    total_count = len(records)

    # Monthly trend
    monthly = {}
    for r in records:
        month = r["incident_date"][:7]  # YYYY-MM
        if month not in monthly:
            monthly[month] = {"count": 0, "amount_usd": 0.0}
        monthly[month]["count"] += 1
        monthly[month]["amount_usd"] += r["amount_usd"]

    monthly_sorted = [
        {"month": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2)}
        for k, v in sorted(monthly.items())
    ]

    # By platform
    platform_agg = {}
    for r in records:
        p = r["platform"]
        if p not in platform_agg:
            platform_agg[p] = {"count": 0, "amount_usd": 0.0}
        platform_agg[p]["count"] += 1
        platform_agg[p]["amount_usd"] += r["amount_usd"]

    by_platform = [
        {"platform": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2)}
        for k, v in sorted(platform_agg.items())
    ]

    # By record type
    type_agg = {}
    for r in records:
        t = r["record_type"]
        if t not in type_agg:
            type_agg[t] = {"count": 0, "amount_usd": 0.0}
        type_agg[t]["count"] += 1
        type_agg[t]["amount_usd"] += r["amount_usd"]

    by_record_type = [
        {"type": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2)}
        for k, v in sorted(type_agg.items(), key=lambda x: -x[1]["amount_usd"])
    ]

    # By merchant (top 15)
    merchant_agg = {}
    for r in records:
        m = r["merchant_account"]
        if m not in merchant_agg:
            merchant_agg[m] = {"count": 0, "amount_usd": 0.0, "platform": r["platform"]}
        merchant_agg[m]["count"] += 1
        merchant_agg[m]["amount_usd"] += r["amount_usd"]

    top_merchants = sorted(merchant_agg.items(), key=lambda x: -x[1]["amount_usd"])[:15]
    by_merchant = [
        {"merchant": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2), "platform": v["platform"]}
        for k, v in top_merchants
    ]

    # By region (from merchant name patterns)
    region_agg = {}
    for r in records:
        region = _infer_region(r["merchant_account"])
        if region not in region_agg:
            region_agg[region] = {"count": 0, "amount_usd": 0.0}
        region_agg[region]["count"] += 1
        region_agg[region]["amount_usd"] += r["amount_usd"]

    by_region = [
        {"region": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2)}
        for k, v in sorted(region_agg.items(), key=lambda x: -x[1]["amount_usd"])
    ]

    # By currency
    currency_agg = {}
    for r in records:
        c = r["currency_original"]
        if c not in currency_agg:
            currency_agg[c] = {"count": 0, "amount_original": 0.0, "amount_usd": 0.0}
        currency_agg[c]["count"] += 1
        currency_agg[c]["amount_original"] += r["amount_original"]
        currency_agg[c]["amount_usd"] += r["amount_usd"]

    by_currency = [
        {
            "currency": k,
            "count": v["count"],
            "amount_original": round(v["amount_original"], 2),
            "amount_usd": round(v["amount_usd"], 2),
        }
        for k, v in sorted(currency_agg.items(), key=lambda x: -x[1]["amount_usd"])
    ]

    # Chargeback vs Fraud vs Other breakdown
    category_agg = {}
    for r in records:
        cat = _categorize_record_type(r["record_type"])
        if cat not in category_agg:
            category_agg[cat] = {"count": 0, "amount_usd": 0.0}
        category_agg[cat]["count"] += 1
        category_agg[cat]["amount_usd"] += r["amount_usd"]

    by_category = [
        {"category": k, "count": v["count"], "amount_usd": round(v["amount_usd"], 2)}
        for k, v in sorted(category_agg.items(), key=lambda x: -x[1]["amount_usd"])
    ]

    return {
        "total_usd": round(total_usd, 2),
        "total_count": total_count,
        "monthly_trend": monthly_sorted,
        "by_platform": by_platform,
        "by_record_type": by_record_type,
        "by_merchant": by_merchant,
        "by_region": by_region,
        "by_currency": by_currency,
        "by_category": by_category,
    }


def _infer_region(merchant: str) -> str:
    """Infer region from merchant account name."""
    m = merchant.upper()
    if "UK" in m:
        return "UK"
    if "USA" in m or "US" in m:
        return "US"
    if "BE" in m:
        return "Belgium"
    if "BR" in m:
        return "Brazil"
    if "CH" in m:
        return "Switzerland"
    if "JPY" in m or "JP" in m:
        return "Japan"
    if "MEX" in m:
        return "Mexico"
    if "CAN" in m:
        return "Canada"
    if "MEL" in m:
        return "Australia"
    if "MUM" in m:
        return "India"
    if "CO" in m:
        return "Colombia"
    return "Other"


def _categorize_record_type(record_type: str) -> str:
    """Categorize record type into high-level buckets."""
    rt = record_type.lower()
    if "fraud" in rt:
        return "Fraud"
    if "reversed" in rt or "won" in rt:
        return "Recovered"
    if "chargeback" in rt or "second" in rt:
        return "Chargeback"
    if "rfi" in rt:
        return "Information Request"
    return "Other"


def main():
    parser = argparse.ArgumentParser(description="Ten Chargeback ETL Pipeline")
    parser.add_argument("--zip", required=True, help="Path to Chargeback Records zip file")
    parser.add_argument("--rates", required=True, help="Path to exchange_rates.json")
    parser.add_argument("--output", required=True, help="Output directory for clean data")

    args = parser.parse_args()
    summary = run_pipeline(args.zip, args.rates, args.output)

    print(f"\n{'='*60}")
    print(f"PIPELINE SUMMARY")
    print(f"{'='*60}")
    print(f"Total records:      {summary['total_records']:,}")
    print(f"Converted to USD:   {summary['total_converted']:,}")
    print(f"Needs review:       {summary['total_needs_review']:,}")
    print(f"Total USD amount:   ${summary['total_usd']:,.2f}")
    print(f"\nBy platform:")
    for p, count in sorted(summary["by_platform"].items()):
        usd = summary["usd_by_platform"].get(p, 0)
        print(f"  {p:12s}: {count:6,} records  ${usd:>12,.2f} USD")
    print(f"\nBy record type:")
    for rt, count in sorted(summary["by_record_type"].items(), key=lambda x: -x[1]):
        print(f"  {rt:30s}: {count:6,}")
    print(f"\nBy currency:")
    for curr, count in sorted(summary["by_currency"].items(), key=lambda x: -x[1]):
        print(f"  {curr:5s}: {count:6,} records")


if __name__ == "__main__":
    main()
