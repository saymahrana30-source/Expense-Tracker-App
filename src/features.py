"""
features.py
-----------
Phase 5: FEATURE ENGINEERING.
We add columns that make analysis easier: month, weekday, weekend flag,
signed amount (income positive, expense negative) and needs/wants group.
"""

import numpy as np

from src.config import NEEDS, WANTS

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def add_features(df):
    """Return a copy of the cleaned table with the extra analysis columns."""
    df = df.copy()
    df["Year"] = df["Date"].dt.year
    df["Month_Num"] = df["Date"].dt.month
    df["Month"] = df["Date"].dt.month_name()
    df["Year_Month"] = df["Date"].dt.strftime("%Y-%m")
    df["Day"] = df["Date"].dt.day
    df["Weekday"] = df["Date"].dt.day_name()
    df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5
    df["Signed_Amount"] = np.where(df["Type"] == "Income", df["Amount"], -df["Amount"])

    # Income, Need, Want or Other (for the 50/30/20 check)
    df["Spend_Group"] = np.where(df["Type"] == "Income", "Income", "Other")
    is_expense = df["Type"] == "Expense"
    df.loc[is_expense & df["Category"].isin(NEEDS), "Spend_Group"] = "Need"
    df.loc[is_expense & df["Category"].isin(WANTS), "Spend_Group"] = "Want"
    return df
