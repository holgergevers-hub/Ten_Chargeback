"""Flexible field extraction for inconsistent merchant platform schemas.

The merchant platforms use varying column names across different merchant
accounts and time periods. This module provides multi-name field lookups.
"""

# Each tuple lists all known column name variants for a logical field.
# The first matching key in the row dict wins.

DATE_FIELDS = ("Date", "Record Date", "Transaction Date")
CURRENCY_FIELDS = ("CurrencyCode", "Curr", "Dispute Currency")
AMOUNT_FIELDS = ("Chargeback Value", "Amount", "Dispute Amount")


def get_field(row: dict, candidates: tuple[str, ...], default: str = "") -> str:
    """Return the value of the first matching field name in the row."""
    for key in candidates:
        val = row.get(key, "").strip()
        if val:
            return val
    return default


def get_amount(row: dict) -> str:
    """Extract the dispute/chargeback amount from a row."""
    return get_field(row, AMOUNT_FIELDS)


def get_currency(row: dict) -> str:
    """Extract the currency code from a row."""
    return get_field(row, CURRENCY_FIELDS)


def get_date(row: dict) -> str:
    """Extract the incident/record date from a row."""
    return get_field(row, DATE_FIELDS)
