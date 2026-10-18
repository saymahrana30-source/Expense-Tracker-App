"""
main.py
-------
RUN THIS FILE to execute the whole project:

    python main.py

Steps:
  1. Create or load the synthetic expense data
  2. Clean the data and report every fix
  3. Add analysis features (month, weekday, needs/wants)
  4. Analyse categories, months, budgets, weekdays and unusual transactions
  5. Draw the charts
  6. Generate plain-English insights
  7. Save every report to outputs/
"""

import json

from src.analysis import (budget_check, budget_pivot, category_month_matrix, category_summary,
                          detect_anomalies, monthly_summary, needs_wants_split, overall_totals,
                          weekday_summary)
from src.config import CURRENCY, OUTPUTS_DIR, PROCESSED_DATA_PATH, RAW_DATA_PATH, ROOT_DIR
from src.data_generator import generate_and_save
from src.features import add_features
from src.insights import generate_insights
from src.preprocessing import clean_expenses, load_raw_data
from src.visualize import (plot_anomalies, plot_budget_heatmap, plot_category_totals,
                           plot_dashboard, plot_expense_pie, plot_monthly_income_expense,
                           plot_monthly_spending_by_category, plot_weekday_activity)


def print_step(title):
    """Print a banner so each step is easy to find in the terminal."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    # ------------------------------------------------------------------
    print_step("STEP 1 | Create or load the synthetic expense data")
    if RAW_DATA_PATH.exists():
        print(f"Found existing data: {RAW_DATA_PATH.relative_to(ROOT_DIR)}")
    else:
        print("No data found, generating a simulated year of expenses...")
        generate_and_save()
    raw = load_raw_data()
    print(f"Loaded {raw.shape[0]} rows x {raw.shape[1]} columns\n")
    print("Data preview (first 5 rows):")
    print(raw.head().to_string(index=False))
    print("\nMissing values per column:")
    print(raw.isna().sum().to_string())
    print("\nCategory values exactly as they appear in the file:")
    print(raw["Category"].dropna().unique().tolist())
    print("\nTransaction types exactly as they appear in the file:")
    print(raw["Type"].dropna().unique().tolist())

    # ------------------------------------------------------------------
    print_step("STEP 2 | Clean the data")
    clean, report = clean_expenses(raw)
    print(f"Rows loaded                            : {report['rows_loaded']}")
    print(f"Exact duplicate rows removed           : {report['exact_duplicates_removed']}")
    print(f"Missing critical fields (before drop)  : {report['missing_critical_fields']}")
    print(f"Rows dropped for missing fields        : {report['rows_dropped_missing_critical']}")
    print(f"Dates in an unreadable format dropped  : {report['unreadable_dates_dropped']}")
    print(f"Invalid amounts dropped                : {report['invalid_amounts_dropped']}")
    print(f"Invalid types dropped                  : {report['invalid_types_dropped']}")
    print(f"Categories standardised                : {report['categories_standardised']}")
    print(f"Types standardised                     : {report['types_standardised']}")
    print(f"Missing descriptions filled            : {report['missing_descriptions_filled']}")
    print(f"Duplicates found after standardising   : {report['duplicates_after_standardising_removed']}")
    print(f"Rows after cleaning                    : {report['rows_after_cleaning']}")
    print(f"Date range                             : {report['date_range'][0]} to {report['date_range'][1]}")
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean.to_csv(PROCESSED_DATA_PATH, index=False, encoding="utf-8")
    print(f"\nCleaned data saved to {PROCESSED_DATA_PATH.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    print_step("STEP 3 | Feature engineering")
    df = add_features(clean)
    print(f"Columns now: {df.shape[1]}")
    print(df[["Date", "Category", "Amount", "Type", "Year_Month", "Weekday", "Spend_Group"]]
          .head().to_string(index=False))

    # ------------------------------------------------------------------
    print_step("STEP 4 | Analysis")
    expenses = df[df["Type"] == "Expense"]
    totals = overall_totals(df)
    print(f"Period: {totals['period_start']} to {totals['period_end']}")
    print(f"Income {CURRENCY}{totals['income']:,.0f} | Expense {CURRENCY}{totals['expense']:,.0f} | "
          f"Savings {CURRENCY}{totals['savings']:,.0f} ({totals['savings_rate_pct']}%)")

    summary = category_summary(expenses)
    print("\nCategory-wise spending:")
    print(summary.to_string())

    monthly = monthly_summary(df)
    print("\nMonth-wise income and expense:")
    print(monthly.to_string())

    weekday = weekday_summary(expenses)
    print("\nSpending by weekday:")
    print(weekday.to_string())

    budget_long = budget_check(expenses)
    over = budget_long[budget_long["Over_Budget"]]
    print(f"\nCategory-months over budget: {len(over)} of {len(budget_long)} checked")
    print(over[["Year_Month", "Category", "Spent", "Budget", "Pct_of_Budget"]].to_string(index=False))

    anomalies = detect_anomalies(expenses)
    print(f"\nUnusually large transactions flagged: {len(anomalies)}")
    print(anomalies[["Date", "Category", "Description", "Amount", "Fence"]].to_string(index=False))

    split = needs_wants_split(df)
    print(f"\n50/30/20 check: needs {split['needs_share']:.1f}% | wants {split['wants_share']:.1f}% | "
          f"savings {split['savings_share']:.1f}% of income")

    # ------------------------------------------------------------------
    print_step("STEP 5 | Charts")
    charts = [
        plot_category_totals(summary),
        plot_expense_pie(summary),
        plot_monthly_income_expense(monthly),
        plot_monthly_spending_by_category(category_month_matrix(expenses)),
        plot_weekday_activity(weekday),
        plot_budget_heatmap(budget_pivot(budget_long)),
        plot_anomalies(expenses, anomalies),
        plot_dashboard(monthly, summary, totals, len(anomalies)),
    ]
    for path in charts:
        print(f"Saved images/{path.name}")

    # ------------------------------------------------------------------
    print_step("STEP 6 | Insights")
    insights = generate_insights(df, expenses, summary, monthly, budget_long,
                                 anomalies, split, totals)
    for number, text in enumerate(insights, start=1):
        print(f"{number}. {text}\n")

    # ------------------------------------------------------------------
    print_step("STEP 7 | Save reports")
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUTPUTS_DIR / "category_summary.csv", encoding="utf-8")
    monthly.to_csv(OUTPUTS_DIR / "monthly_summary.csv", encoding="utf-8")
    weekday.to_csv(OUTPUTS_DIR / "weekday_summary.csv", encoding="utf-8")
    budget_long.to_csv(OUTPUTS_DIR / "budget_check.csv", index=False, encoding="utf-8")
    anomalies.to_csv(OUTPUTS_DIR / "unusual_transactions.csv", index=False, encoding="utf-8")
    (OUTPUTS_DIR / "insights.txt").write_text(
        "\n\n".join(f"{n}. {t}" for n, t in enumerate(insights, start=1)), encoding="utf-8")
    with open(OUTPUTS_DIR / "cleaning_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    metrics = {
        **{k: (float(v) if isinstance(v, float) else v) for k, v in totals.items()},
        "top_category": str(summary.index[0]),
        "needs_share_pct": round(float(split["needs_share"]), 1),
        "wants_share_pct": round(float(split["wants_share"]), 1),
        "savings_share_pct": round(float(split["savings_share"]), 1),
        "category_months_over_budget": int(len(over)),
        "unusual_transactions": int(len(anomalies)),
    }
    with open(OUTPUTS_DIR / "metrics.json", "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
    print("Saved to outputs/: category_summary.csv, monthly_summary.csv, weekday_summary.csv,")
    print("                   budget_check.csv, unusual_transactions.csv, insights.txt,")
    print("                   cleaning_report.json, metrics.json")

    # ------------------------------------------------------------------
    print_step("DONE")
    print("Cleaned data : data/processed/cleaned_expenses.csv")
    print("Charts       : images/")
    print("Reports      : outputs/")


if __name__ == "__main__":
    main()
