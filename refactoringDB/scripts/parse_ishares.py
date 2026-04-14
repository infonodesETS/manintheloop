#!/usr/bin/env python3
"""
parse_ishares.py — Parse iShares ETF CSV holdings files.

iShares CSVs have a multi-row metadata header before the actual column headers.
This module finds the real header row (starts with "Ticker,"), parses all equity
rows, and returns normalized dicts.

Usage as module:
    from parse_ishares import parse_csv
    rows = parse_csv("rawdata/ishares_metals_mining_gics151040.csv",
                     etf_name="iShares MSCI Global Metals & Mining Producers ETF",
                     etf_ticker="PICK",
                     gics_code="151040")

Usage as CLI (prints JSON):
    python3 parse_ishares.py <csvfile> --etf-name "..." --etf-ticker "..." --gics-code "..."
"""

import csv
import json
import argparse
import os
import re
import sys


# Legal suffixes to strip when building a normalized name for deduplication.
# Applied in order (longest first) to avoid partial matches.
_LEGAL_SUFFIXES = [
    r"\bCORPORATION\b",
    r"\bCORP\b",
    r"\bLIMITED\b",
    r"\bLTD\b",
    r"\bINCORPORATED\b",
    r"\bINC\b",
    r"\bPUBLIC LIMITED COMPANY\b",
    r"\bPLC\b",
    r"\bSOCIETE ANONYME\b",
    r"\bS\.A\.\b",
    r"\bS\.A\b",
    r"\bNAAMLOZE VENNOOTSCHAP\b",
    r"\bN\.V\.\b",
    r"\bN\.V\b",
    r"\bNV\b",
    r"\bAKTIENGESELLSCHAFT\b",
    r"\bAG\b",
    r"\bSE\b",
    r"\bSPA\b",
    r"\bS\.P\.A\.\b",
    r"\bAB\b",
    r"\bASA\b",
    r"\bOYJ\b",
    r"\bOY\b",
    r"\bCOMPANY\b",
    r"\bCO\b",
    r"\bGROUP\b",
    r"\bHOLDINGS\b",
    r"\bHOLDING\b",
    r"\bINTERNATIONAL\b",
    r"\bINTL\b",
    r"\bSH\b",        # e.g. "CIA VALE DO RIO DOCE SH"
    r"\bCIA\b",       # Compañía
    r"\bGMBH\b",
    r"\bKGAA\b",
]


def normalize_name(raw: str) -> str:
    """
    Strip legal suffixes and normalize for deduplication.
    Returns uppercase with extra whitespace collapsed.
    """
    s = raw.upper().strip()
    for pattern in _LEGAL_SUFFIXES:
        s = re.sub(pattern, "", s)
    # Remove trailing punctuation and whitespace
    s = re.sub(r"[,.\-]+$", "", s).strip()
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s).strip()
    return s


def display_name(raw: str) -> str:
    """
    Convert ALL-CAPS CSV name to title case with legal suffixes stripped.
    e.g. "BHP GROUP LTD" → "BHP Group"
    """
    stripped = normalize_name(raw)
    # Title-case word by word, but keep known all-caps acronyms
    words = stripped.split()
    titled = []
    for w in words:
        # Keep if it looks like an acronym (all letters, ≤4 chars)
        if w.isalpha() and len(w) <= 4:
            titled.append(w)
        else:
            titled.append(w.capitalize())
    return " ".join(titled)


def parse_float(val: str) -> float | None:
    """Parse a numeric string that may contain commas."""
    if not val or not val.strip() or val.strip() == "-":
        return None
    try:
        return float(val.replace(",", ""))
    except ValueError:
        return None


def parse_csv(
    filepath: str,
    etf_name: str,
    etf_ticker: str,
    gics_code: str,
    extracted_at: str | None = None,
) -> list[dict]:
    """
    Parse an iShares ETF CSV file and return a list of equity holding dicts.

    Each dict contains:
        name            - display name (title case, legal suffixes stripped)
        name_raw        - original name from CSV (ALL CAPS)
        name_key        - normalized key for deduplication
        stock_ticker    - ticker symbol from CSV
        stock_sector    - GICS sector from CSV (e.g. "Materials", "Information Technology")
        weight_pct      - portfolio weight as float (e.g. 12.25)
        location        - country of domicile
        exchange        - exchange name
        currency        - trading currency
        etf_name        - ETF full name
        etf_ticker      - ETF ticker
        gics_code       - ETF GICS classification code (e.g. "151040", "45", "50")
        extracted_at    - extraction date (YYYY-MM-DD)
        source_file     - basename of source CSV
    """
    if extracted_at is None:
        from datetime import date
        extracted_at = date.today().isoformat()

    with open(filepath, encoding="utf-8-sig") as f:
        lines = f.readlines()

    # Find the real header row (starts with "Ticker,")
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Ticker,"):
            header_idx = i
            break

    if header_idx is None:
        raise ValueError(f"Could not find header row in {filepath}")

    reader = csv.DictReader(lines[header_idx:])
    results = []

    for row in reader:
        # Skip non-equity rows (Cash, Money Market, Futures, etc.)
        # Use `or ""` to handle None values from short/malformed footer rows
        if (row.get("Asset Class") or "").strip() != "Equity":
            continue

        name_raw = (row.get("Name") or "").strip()
        if not name_raw:
            continue

        results.append({
            "name": display_name(name_raw),
            "name_raw": name_raw,
            "name_key": normalize_name(name_raw),
            "stock_ticker": row.get("Ticker", "").strip(),
            "stock_sector": row.get("Sector", "").strip() or None,
            "weight_pct": parse_float(row.get("Weight (%)", "")),
            "location": row.get("Location", "").strip() or None,
            "exchange": row.get("Exchange", "").strip() or None,
            "currency": row.get("Currency", "").strip() or None,
            "etf_name": etf_name,
            "etf_ticker": etf_ticker,
            "gics_code": gics_code,
            "extracted_at": extracted_at,
            "source_file": os.path.basename(filepath),
        })

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse an iShares ETF CSV file to JSON")
    parser.add_argument("filepath", help="Path to the iShares CSV file")
    parser.add_argument("--etf-name", required=True, help="Full ETF name")
    parser.add_argument("--etf-ticker", required=True, help="ETF ticker symbol")
    parser.add_argument("--gics-code", required=True, help="GICS code for this ETF")
    parser.add_argument("--extracted-at", help="Extraction date YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    rows = parse_csv(
        args.filepath,
        etf_name=args.etf_name,
        etf_ticker=args.etf_ticker,
        gics_code=args.gics_code,
        extracted_at=args.extracted_at,
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"\n# {len(rows)} equity rows", file=sys.stderr)
