"""Convert chargeback amounts to USD using exchange rate data."""

import json
from datetime import datetime, timedelta
from pathlib import Path


class CurrencyConverter:
    """Converts amounts to USD using daily exchange rates.

    The exchange_rates.json file maps dates to {currency: rate} where
    rate is the amount of foreign currency per 1 USD.
    So to convert foreign amount to USD: amount_usd = amount / rate.
    For USD amounts, no conversion needed (rate = 1.0).
    """

    def __init__(self, rates_path: str):
        with open(rates_path, "r", encoding="utf-8") as f:
            self._rates = json.load(f)
        # Pre-sort dates for nearest-date lookup
        self._sorted_dates = sorted(self._rates.keys())
        # Track supported currencies from first entry
        if self._sorted_dates:
            self._supported = set(self._rates[self._sorted_dates[0]].keys())
        else:
            self._supported = set()

    @property
    def supported_currencies(self) -> set:
        return self._supported

    def _find_nearest_date(self, date_str: str) -> str | None:
        """Find the nearest available date, searching backward first."""
        if date_str in self._rates:
            return date_str

        try:
            target = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

        # Search backward up to 30 days
        for days_back in range(1, 31):
            candidate = (target - timedelta(days=days_back)).strftime("%Y-%m-%d")
            if candidate in self._rates:
                return candidate

        # Search forward up to 30 days
        for days_fwd in range(1, 31):
            candidate = (target + timedelta(days=days_fwd)).strftime("%Y-%m-%d")
            if candidate in self._rates:
                return candidate

        return None

    def convert(self, amount: float, currency: str, date_str: str) -> tuple[float, float, str]:
        """Convert an amount to USD.

        Args:
            amount: The original amount in the source currency.
            currency: The 3-letter currency code (e.g. GBP, EUR).
            date_str: The date for rate lookup (YYYY-MM-DD).

        Returns:
            (amount_usd, exchange_rate, status) where status is one of:
            - "converted" — successful conversion
            - "base_currency" — already USD, no conversion needed
            - "rate_not_found" — currency not in exchange rates
            - "date_not_found" — no rate available for date range
        """
        currency = currency.upper().strip()

        if currency == "USD":
            return amount, 1.0, "base_currency"

        if currency not in self._supported:
            return 0.0, 0.0, "rate_not_found"

        rate_date = self._find_nearest_date(date_str)
        if rate_date is None:
            return 0.0, 0.0, "date_not_found"

        rate = self._rates[rate_date].get(currency)
        if rate is None or rate == 0:
            return 0.0, 0.0, "rate_not_found"

        amount_usd = round(amount / rate, 2)
        return amount_usd, rate, "converted"


def convert_records(records: list[dict], converter: CurrencyConverter) -> tuple[list[dict], list[dict]]:
    """Convert all records to USD.

    Returns:
        (converted_records, needs_review_records)
    """
    converted = []
    needs_review = []

    for record in records:
        amount = record["amount_original"]
        currency = record["currency_original"]
        date_str = record["incident_date"]

        amount_usd, rate, status = converter.convert(amount, currency, date_str)

        record["amount_usd"] = amount_usd
        record["exchange_rate"] = rate

        if status in ("rate_not_found", "date_not_found"):
            record["_conversion_status"] = status
            needs_review.append(record)
        else:
            converted.append(record)

    return converted, needs_review
