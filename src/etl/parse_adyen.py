"""Parse Adyen CSV dispute reports (comma-delimited).

Column names vary across merchant accounts:
  Date field:     "Date" | "Record Date" | "Transaction Date"
  Currency field:  "CurrencyCode" | "Curr" | "Dispute Currency"
  Amount field:    "Chargeback Value" | "Amount" | "Dispute Amount"
"""

import csv
from pathlib import Path

from .field_mapping import get_amount


def parse(filepath: Path) -> list[dict]:
    """Parse a single Adyen CSV file. Returns list of row dicts.

    Skips files that contain only headers (no data rows).
    """
    records = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                value = get_amount(row)
                if not value:
                    continue
                try:
                    float(value)
                except ValueError:
                    continue
                records.append(dict(row))
    except Exception:
        pass
    return records


def parse_all(file_list: list[Path]) -> list[dict]:
    """Parse all Adyen CSV files from a merchant directory."""
    all_records = []
    for fp in file_list:
        all_records.extend(parse(fp))
    return all_records
