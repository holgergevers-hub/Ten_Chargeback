"""Parse Ingenico JSON dispute reports.

Column names can vary:
  Currency field:  "Dispute Currency" | "CurrencyCode" | "Curr"
  Amount field:    "Chargeback Value" | "Amount" | "Dispute Amount"
"""

import json
from pathlib import Path

from .field_mapping import get_amount


def parse(filepath: Path) -> list[dict]:
    """Parse a single Ingenico JSON file. Returns list of row dicts.

    Skips files that are empty or contain an empty array.
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read().strip()
            if not content or content == "[]":
                return []
            data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    records = []
    for row in data:
        value = get_amount(row)
        if not value:
            continue
        try:
            float(value)
        except ValueError:
            continue
        records.append(row)
    return records


def parse_all(file_list: list[Path]) -> list[dict]:
    """Parse all Ingenico JSON files from a merchant directory."""
    all_records = []
    for fp in file_list:
        all_records.extend(parse(fp))
    return all_records
