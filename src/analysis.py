"""
analysis.py
-----------
Phase 6: ANALYSIS. Every number the dashboard and insights use comes from here.

  overall_totals          income, expense, savings and savings rate for the whole year
  category_summary        total, share, count and average for each category
  monthly_summary         income, expense and savings for each month
  category_month_matrix   expense by month (rows) and category (columns), for charts
  weekday_summary         how many transactions and how much money on each weekday
  budget_check            spending against the monthly budget, for each category and month
  budget_pivot            the budget check as a grid, for the heatmap
  detect_anomalies        transactions far above normal for their category (IQR rule)
  needs_wants_split       the 50/30/20 check: needs, wants and savings as % of income
"""

import numpy as np
import pandas as pd

from src.config import (ANOMALY_IQR_MULTIPLIER, MIN_ROWS_FOR_ANOMALY_CHECK, MONTHLY_BUDGETS,
                        OVERSPEND_TOLERANCE)
from src.features import WEEKDAY_ORDER


def overall_totals(df):
    income = float(df.loc[df["Type"] == "Income", "Amount"].sum())
    expense = float(df.loc[df["Type"] == "Expense", "Amount"].sum())
    savings = income - expense
    return {
        "income": income,
        "expense": expense,
        "savings": savings,
        "savings_rate_pct": round(savings / income * 100, 1) if income else 0.0,
        "transactions": int(len(df)),
        "period_start": df["Date"].min().strftime("%d %b %Y"),
        "period_end": df["Date"].max().strftime("%d %b %Y"),
    }


def category_summary(expenses):
    grouped = expenses.groupby("Category")["Amount"]
    summary = pd.DataFrame({
        "Total": grouped.sum(),
        "Transactions": grouped.count(),
        "Average": grouped.mean().round(0),
        "Largest": grouped.max(),
    })
    summary["Share_%"] = (summary["Total"] / summary["Total"].sum() * 100).round(1)
    return summary.sort_values("Total", ascending=False)


def monthly_summary(df):
    income = df.loc[df["Type"] == "Income"].groupby("Year_Month")["Amount"].sum()
    expense = df.loc[df["Type"] == "Expense"].groupby("Year_Month")["Amount"].sum()
    monthly = pd.DataFrame({"Income": income, "Expense": expense}).fillna(0)
    monthly["Savings"] = monthly["Income"] - monthly["Expense"]
    monthly["Savings_Rate_%"] = (monthly["Savings"] / monthly["Income"].replace(0, np.nan) * 100).round(1)
    monthly["Expense_Change_%"] = (monthly["Expense"].pct_change() * 100).round(1)
    return monthly


def category_month_matrix(expenses):
    matrix = expenses.pivot_table(index="Year_Month", columns="Category", values="Amount",
                                  aggfunc="sum", fill_value=0)
    column_order = matrix.sum().sort_values(ascending=False).index
    return matrix[column_order]


def weekday_summary(expenses):
    grouped = expenses.groupby("Weekday")["Amount"].agg(Transactions="count", Total_Spent="sum")
    return grouped.reindex(WEEKDAY_ORDER).fillna(0).astype({"Transactions": int})


def budget_check(expenses, budgets=MONTHLY_BUDGETS, tolerance=OVERSPEND_TOLERANCE):
    """Compare spending with the budget for every category and month that has transactions."""
    spent = expenses.groupby(["Year_Month", "Category"])["Amount"].sum().reset_index(name="Spent")
    spent = spent[spent["Category"].isin(budgets.keys())].copy()
    spent["Budget"] = spent["Category"].map(budgets)
    spent["Pct_of_Budget"] = (spent["Spent"] / spent["Budget"] * 100).round(1)
    spent["Over_Budget"] = spent["Spent"] > spent["Budget"] * (1 + tolerance)
    return spent.sort_values(["Year_Month", "Category"]).reset_index(drop=True)


def budget_pivot(budget_long):
    """Rows = categories, columns = months, values = % of budget used."""
    return budget_long.pivot(index="Category", columns="Year_Month", values="Pct_of_Budget")


def detect_anomalies(expenses):
    """
    Flag transactions that are far above normal for their category.
    Rule: amount > Q3 + 3 x IQR, where IQR = Q3 - Q1, calculated within each category.
    This method is robust because a few large values do not change the quartiles much.
    """
    flagged = []
    for category, group in expenses.groupby("Category"):
        if len(group) < MIN_ROWS_FOR_ANOMALY_CHECK:
            continue
        q1, q3 = group["Amount"].quantile([0.25, 0.75])
        upper_fence = q3 + ANOMALY_IQR_MULTIPLIER * (q3 - q1)
        hits = group[group["Amount"] > upper_fence].copy()
        hits["Fence"] = round(upper_fence, 0)
        flagged.append(hits)
    if not flagged:
        return expenses.iloc[0:0].assign(Fence=np.nan)
    return pd.concat(flagged).sort_values("Amount", ascending=False)


def needs_wants_split(df):
    """The 50/30/20 check. Needs should be 50% or less of income, wants 30% or less, savings 20% or more."""
    income = float(df.loc[df["Type"] == "Income", "Amount"].sum())
    expenses = df.loc[df["Type"] == "Expense"]
    needs = float(expenses.loc[expenses["Spend_Group"] == "Need", "Amount"].sum())
    wants = float(expenses.loc[expenses["Spend_Group"] == "Want", "Amount"].sum())
    total_expense = float(expenses["Amount"].sum())
    savings = income - total_expense
    return {
        "income": income,
        "needs": needs,
        "wants": wants,
        "savings": savings,
        "needs_share": needs / income * 100,
        "wants_share": wants / income * 100,
        "savings_share": savings / income * 100,
    }
