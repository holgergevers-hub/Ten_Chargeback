"""Parse Stripe dispute reports (pipe-delimited OR tab-delimited text files).

The delimiter varies across merchant accounts:
  Some use pipe (|), others use tab (\\t).

Column names also vary:
  Date field:     "Date" | "Record Date" | "Transaction Date"
  Currency field:  "Dispute Currency" | "CurrencyCode" | "Curr"
  Amount field:    "Amount" | "Chargeback Value" | "Dispute Amount"
"""

import csv
from pathlib import Path

from .field_mapping import get_amount


def _detect_delimiter(header_line: str) -> str:
    """Detect whether the file uses pipe or tab delimiters."""
    pipe_count = header_line.count("|")
    tab_count = header_line.count("\t")
    if pipe_count > tab_count:
        return "|"
    return "\t"


def parse(filepath: Path) -> list[dict]:
    """Parse a single Stripe delimited file. Returns list of row dicts.

    Auto-detects delimiter (pipe vs tab).
    Skips files that contain only headers.
    """
    records = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            first_line = f.readline()
            if not first_line.strip():
                return []
            delimiter = _detect_delimiter(first_line)
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
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
    """Parse all Stripe files from a merchant directory."""
    all_records = []
    for fp in file_list:
        all_records.extend(parse(fp))
    return all_records
