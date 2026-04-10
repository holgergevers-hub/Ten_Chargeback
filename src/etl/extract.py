"""Extract chargeback data from the merchant statements zip archive."""

import zipfile
from pathlib import Path


def extract_zip(zip_path: str, output_dir: str) -> dict:
    """Extract the zip and return a manifest grouped by platform.

    Returns:
        {
            "Adyen":    {"format": "csv",  "merchants": {"TenMexMerEcom": [path, ...], ...}},
            "Ingenico": {"format": "json", "merchants": {"TenUK1_USD": [path, ...], ...}},
            "Stripe":   {"format": "pipe", "merchants": {"TENBR1": [path, ...], ...}},
        }
    """
    zip_path = Path(zip_path)
    output_dir = Path(output_dir)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(output_dir)

    platform_formats = {
        "Adyen": "csv",
        "Ingenico": "json",
        "Stripe": "pipe",
    }

    manifest = {}
    root = output_dir / "Chargeback Records"

    for platform, fmt in platform_formats.items():
        platform_dir = root / platform
        if not platform_dir.is_dir():
            continue

        merchants = {}
        for merchant_dir in sorted(platform_dir.iterdir()):
            if not merchant_dir.is_dir():
                continue
            files = sorted(merchant_dir.glob("*"))
            data_files = [f for f in files if f.is_file()]
            if data_files:
                merchants[merchant_dir.name] = data_files

        manifest[platform] = {"format": fmt, "merchants": merchants}

    return manifest


def get_exchange_rates_path(zip_path: str, output_dir: str) -> Path:
    """Return the path to exchange_rates.json after extraction."""
    return Path(output_dir) / "Chargeback Records" / "exchange_rates.json"
