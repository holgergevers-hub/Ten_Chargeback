"""Normalize records from all platforms into a unified schema.

Handles inconsistent column names and date formats across merchant accounts
using flexible field lookups and auto-detection.
"""

from datetime import datetime

from .field_mapping import get_field, get_amount, get_currency, get_date, DATE_FIELDS, CURRENCY_FIELDS, AMOUNT_FIELDS


# Unified output schema:
UNIFIED_FIELDS = [
    "incident_date",        # YYYY-MM-DD
    "platform",             # Adyen | Ingenico | Stripe
    "merchant_account",     # e.g. TenUK1_USD
    "company_account",      # e.g. TenLifManLim
    "psp_reference",        # Platform transaction reference
    "payment_method",       # visa, mc, amex, etc.
    "currency_original",    # Original dispute currency code
    "amount_original",      # Original dispute amount (float)
    "record_type",          # Normalized record type
    "dispute_reason",       # Human-readable reason
    "cb_scheme_code",       # Chargeback scheme (visa, mc, etc.)
    "cb_reason_code",       # Chargeback reason code
    "shopper_country",      # 2-letter country code
    "issuer_country",       # 2-letter country code
    "payment_date",         # YYYY-MM-DD
    "payment_currency",     # Payment currency code
    "payment_amount",       # Payment amount (float)
    "dispute_date",         # YYYY-MM-DD
    "dispute_end_date",     # YYYY-MM-DD
    "risk_scoring",         # Numeric risk score
    "shopper_interaction",  # Ecommerce, POS, MOTO, etc.
    "dispute_psp_reference",# Dispute-specific reference
    "amount_usd",           # Converted to USD (filled by currency_converter)
    "exchange_rate",        # Rate used for conversion
]

# Record type normalization mapping
RECORD_TYPE_MAP = {
    "notificationofchargeback": "Chargeback",
    "notificationoffraud": "Fraud",
    "chargeback": "Chargeback",
    "chargebackreversed": "Reversed",
    "secondchargeback": "Second Chargeback",
    "requestforinformation": "RFI",
    "informationsupplied": "Information Supplied",
    "chargebackexternallyadjudicated": "Externally Adjudicated",
    "prearbitrationwon": "Pre-Arb Won",
    "prearbitrationlost": "Pre-Arb Lost",
}

# Date formats to try in order
_DATE_FORMATS = [
    "%Y-%m-%d",   # 2024-04-22
    "%d-%m-%Y",   # 22-04-2024
    "%m/%d/%Y",   # 04/22/2024
    "%d/%m/%Y",   # 22/04/2024
    "%Y/%m/%d",   # 2024/04/22
]


def _parse_date(date_str: str) -> str:
    """Auto-detect date format and parse to YYYY-MM-DD."""
    date_str = date_str.strip()
    if not date_str:
        return ""
    # Take only the date part (strip time)
    date_part = date_str.split(" ")[0]
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(date_part, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return date_str


def _normalize_record_type(raw: str) -> str:
    """Normalize record type to a standard value."""
    key = raw.strip().lower().replace(" ", "").replace("_", "")
    return RECORD_TYPE_MAP.get(key, raw.strip())


def _safe_float(val: str) -> float:
    """Convert string to float, returning 0.0 on failure."""
    try:
        return float(str(val).strip())
    except (ValueError, AttributeError):
        return 0.0


def normalize_record(row: dict, platform: str, merchant_name: str) -> dict:
    """Normalize a single record from any platform to the unified schema.

    Uses flexible field lookups to handle inconsistent column names.
    Auto-detects date format.
    """
    return {
        "incident_date": _parse_date(get_date(row)),
        "platform": platform,
        "merchant_account": row.get("Merchant Account", merchant_name).strip(),
        "company_account": row.get("Company Account", "").strip(),
        "psp_reference": row.get("Psp Reference", "").strip(),
        "payment_method": row.get("Payment Method", "").strip(),
        "currency_original": get_currency(row).upper(),
        "amount_original": _safe_float(get_amount(row)),
        "record_type": _normalize_record_type(row.get("Record Type", "")),
        "dispute_reason": row.get("Dispute Reason", "").strip(),
        "cb_scheme_code": row.get("CB Scheme Code", "").strip(),
        "cb_reason_code": row.get("CB Reason Code", "").strip(),
        "shopper_country": row.get("Shopper Country", "").strip().upper(),
        "issuer_country": row.get("Issuer Country", "").strip().upper(),
        "payment_date": _parse_date(row.get("Payment Date", "")),
        "payment_currency": row.get("Payment Currency", "").strip().upper(),
        "payment_amount": _safe_float(row.get("Payment Amount", "0")),
        "dispute_date": _parse_date(row.get("Dispute Date", "")),
        "dispute_end_date": _parse_date(row.get("Dispute End Date", "")),
        "risk_scoring": row.get("Risk Scoring", "").strip(),
        "shopper_interaction": row.get("Shopper Interaction", "").strip(),
        "dispute_psp_reference": row.get("Dispute PSP Reference", "").strip(),
        "amount_usd": 0.0,
        "exchange_rate": 0.0,
    }


# Backward-compatible aliases used by pipeline.py
def normalize_adyen(row: dict, merchant_name: str) -> dict:
    return normalize_record(row, "Adyen", merchant_name)


def normalize_ingenico(row: dict, merchant_name: str) -> dict:
    return normalize_record(row, "Ingenico", merchant_name)


def normalize_stripe(row: dict, merchant_name: str) -> dict:
    return normalize_record(row, "Stripe", merchant_name)
