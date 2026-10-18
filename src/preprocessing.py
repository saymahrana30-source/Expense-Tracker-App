"""
preprocessing.py
----------------
Phase 3: DATA CLEANING.

Order of the steps matters:
  1. Load every column as TEXT, so the messy values are visible exactly as they are
  2. Remove exact duplicate rows
  3. Drop rows that are missing a critical field (Date, Amount, Category, Type)
  4. Convert dates (two formats are accepted) and amounts (₹ and commas removed)
  5. Standardise text: spaces, capital letters, payment method names
  6. Remove duplicates again, because some rows only match after standardising
  7. Count every fix in a report, so the numbers can be explained in an interview
"""

import pandas as pd

from src.config import RAW_DATA_PATH

CRITICAL_COLUMNS = ["Date", "Amount", "Category", "Type"]
VALID_TYPES = {"Income", "Expense"}
PAYMENT_METHOD_NAMES = {
    "upi": "UPI",
    "card": "Card",
    "cash": "Cash",
    "net banking": "Net Banking",
    "netbanking": "Net Banking",
}


def load_raw_data(path=RAW_DATA_PATH):
    """Read the CSV with every column as text, so nothing is changed before we check it."""
    df = pd.read_csv(path, dtype=str, encoding="utf-8")
    df.columns = [c.strip() for c in df.columns]
    return df


def parse_dates(text):
    """Accept 2024-05-31 and 31/05/2024. Anything else becomes NaT (missing)."""
    text = text.str.strip()
    iso = pd.to_datetime(text, format="%Y-%m-%d", errors="coerce")
    day_first = pd.to_datetime(text, format="%d/%m/%Y", errors="coerce")
    return iso.fillna(day_first)


def parse_amounts(text):
    """Turn '₹1,250' or ' 980 ' into numbers. Anything unreadable becomes NaN."""
    cleaned = (text.astype(str)
               .str.replace("₹", "", regex=False)
               .str.replace(",", "", regex=False)
               .str.strip())
    return pd.to_numeric(cleaned, errors="coerce")


def clean_expenses(raw):
    """
    Clean the raw transactions.
    Returns (cleaned DataFrame, report dictionary with the count of every fix).
    """
    report = {"rows_loaded": int(len(raw))}
    df = raw.copy()

    # 1. Exact duplicate rows
    before = len(df)
    df = df.drop_duplicates()
    report["exact_duplicates_removed"] = before - len(df)

    # 2. Missing critical fields (counted first, then dropped)
    report["missing_critical_fields"] = {c: int(df[c].isna().sum()) for c in CRITICAL_COLUMNS}
    before = len(df)
    df = df.dropna(subset=CRITICAL_COLUMNS)
    report["rows_dropped_missing_critical"] = before - len(df)

    # 3. Dates
    df["Date"] = parse_dates(df["Date"])
    bad = df["Date"].isna()
    report["unreadable_dates_dropped"] = int(bad.sum())
    df = df[~bad].copy()

    # 4. Amounts must be numbers above zero
    df["Amount"] = parse_amounts(df["Amount"])
    bad = df["Amount"].isna() | (df["Amount"] <= 0)
    report["invalid_amounts_dropped"] = int(bad.sum())
    df = df[~bad].copy()

    # 5. Text fields
    original_category = df["Category"]
    df["Category"] = df["Category"].str.strip().str.title()
    report["categories_standardised"] = int((original_category != df["Category"]).sum())

    original_type = df["Type"]
    df["Type"] = df["Type"].str.strip().str.title()
    report["types_standardised"] = int((original_type != df["Type"]).sum())
    bad = ~df["Type"].isin(VALID_TYPES)
    report["invalid_types_dropped"] = int(bad.sum())
    df = df[~bad].copy()

    report["missing_descriptions_filled"] = int(df["Description"].isna().sum())
    df["Description"] = df["Description"].fillna("Not provided").str.strip()

    payment = df["Payment_Method"].fillna("Unknown").str.strip().str.lower()
    df["Payment_Method"] = payment.map(PAYMENT_METHOD_NAMES).fillna(payment.str.title())

    # 6. Duplicates that only matched after standardising
    before = len(df)
    df = df.drop_duplicates(subset=["Date", "Category", "Description", "Amount", "Type", "Payment_Method"])
    report["duplicates_after_standardising_removed"] = before - len(df)

    df = df.sort_values("Date").reset_index(drop=True)
    report["rows_after_cleaning"] = int(len(df))
    report["date_range"] = [df["Date"].min().strftime("%Y-%m-%d"), df["Date"].max().strftime("%Y-%m-%d")]
    return df, report
