"""
insights.py
-----------
Phase 8: INSIGHTS. Turns the numbers from analysis.py into plain-English sentences
that a student, manager or non-technical person can read.
Every sentence is built from the data, so the text changes if the data changes.
"""

import pandas as pd

from src.config import CURRENCY, OVERSPEND_TOLERANCE


def _month_label(year_month):
    """Turn '2025-01' into 'January 2025' so the text reads naturally."""
    return pd.Timestamp(f"{year_month}-01").strftime("%B %Y")


def generate_insights(df, expenses, summary, monthly, budget_long, anomalies, split, totals):
    insights = []

    # 1. Headline
    insights.append(
        f"Between {totals['period_start']} and {totals['period_end']} you earned "
        f"{CURRENCY}{totals['income']:,.0f} and spent {CURRENCY}{totals['expense']:,.0f}. "
        f"That leaves {CURRENCY}{totals['savings']:,.0f} saved, a savings rate of "
        f"{totals['savings_rate_pct']:.1f}%."
    )

    # 2. Biggest category
    top = summary.index[0]
    insights.append(
        f"{top} is the biggest expense at {CURRENCY}{summary.loc[top, 'Total']:,.0f}, which is "
        f"{summary.loc[top, 'Share_%']:.1f}% of all spending. The top three categories make up "
        f"{summary['Share_%'].head(3).sum():.1f}% together."
    )

    # 3. Highest and lowest spending months
    peak = monthly["Expense"].idxmax()
    quietest = monthly["Expense"].idxmin()
    insights.append(
        f"Spending was highest in {_month_label(peak)} ({CURRENCY}{monthly.loc[peak, 'Expense']:,.0f}) and "
        f"lowest in {_month_label(quietest)} ({CURRENCY}{monthly.loc[quietest, 'Expense']:,.0f})."
    )

    # 4. Overspending against budget
    over = budget_long[budget_long["Over_Budget"]]
    tolerance_text = f"{OVERSPEND_TOLERANCE:.0%}"
    if over.empty:
        insights.append(f"No category went more than {tolerance_text} over its monthly budget.")
    else:
        counts = over.groupby("Category").size().sort_values(ascending=False)
        counts_text = ", ".join(f"{cat} ({n} month{'s' if n > 1 else ''})" for cat, n in counts.items())
        worst = over.sort_values("Pct_of_Budget", ascending=False).iloc[0]
        insights.append(
            f"{len(over)} category-months went more than {tolerance_text} over budget. Categories "
            f"affected: {counts_text}. The worst case was {worst['Category']} in {_month_label(worst['Year_Month'])}, "
            f"at {worst['Pct_of_Budget']:.0f}% of its budget."
        )

    # 5. Weekend versus weekday spending, per day
    days = pd.date_range(df["Date"].min(), df["Date"].max())
    weekend_days = int((days.dayofweek >= 5).sum())
    weekday_days = len(days) - weekend_days
    weekend_per_day = expenses.loc[expenses["Is_Weekend"], "Amount"].sum() / weekend_days
    weekday_per_day = expenses.loc[~expenses["Is_Weekend"], "Amount"].sum() / weekday_days
    insights.append(
        f"On an average weekend day you spend {CURRENCY}{weekend_per_day:,.0f}, compared with "
        f"{CURRENCY}{weekday_per_day:,.0f} on an average weekday, which is "
        f"{weekend_per_day / weekday_per_day:.1f} times as much."
    )

    # 6. Unusually large transactions
    if anomalies.empty:
        insights.append("No transaction was unusually large compared with others in its category.")
    else:
        examples = "; ".join(
            f"{r.Date:%d %b %Y} {r.Category} ({r.Description}) {CURRENCY}{r.Amount:,.0f}"
            for r in anomalies.head(3).itertuples()
        )
        insights.append(
            f"{len(anomalies)} transactions were far above normal for their category, for example: "
            f"{examples}. Review these first when you plan next year's budget."
        )

    # 7. The 50/30/20 budgeting guideline
    checks = {
        "needs": (split["needs_share"] <= 50,
                  f"needs {split['needs_share']:.1f}% of income (guideline: 50% or less)"),
        "wants": (split["wants_share"] <= 30,
                  f"wants {split['wants_share']:.1f}% of income (guideline: 30% or less)"),
        "savings": (split["savings_share"] >= 20,
                    f"savings {split['savings_share']:.1f}% of income (guideline: 20% or more)"),
    }
    failed = [text for ok, text in checks.values() if not ok]
    status = "All three targets are met." if not failed else "Targets missed: " + "; ".join(failed) + "."
    insights.append("Against the 50/30/20 budgeting guideline, " + "; ".join(t for _, t in checks.values())
                    + ". " + status)

    # 8. Direction of spending over the year
    first_three = monthly["Expense"].iloc[:3].mean()
    last_three = monthly["Expense"].iloc[-3:].mean()
    change = (last_three - first_three) / first_three * 100
    direction = "higher" if change > 0 else "lower"
    insights.append(
        f"The average monthly expense in {_month_label(monthly.index[-3])} to {_month_label(monthly.index[-1])} was "
        f"{abs(change):.1f}% {direction} than in {_month_label(monthly.index[0])} to {_month_label(monthly.index[2])}."
    )
    return insights
