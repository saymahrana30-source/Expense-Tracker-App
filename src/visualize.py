"""
visualize.py
------------
Phase 7: VISUALIZATION. Every chart is saved as a PNG in images/.
Matplotlib draws the charts, and Seaborn is used for the bar charts.
"""

import matplotlib

matplotlib.use("Agg")  # save charts to files, no pop-up windows
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.config import CURRENCY, IMAGES_DIR

sns.set_theme(style="whitegrid")
PALETTE = ["#1565C0", "#2E7D32", "#F9A825", "#C62828", "#6A1B9A",
           "#00838F", "#EF6C00", "#5D4037", "#AD1457", "#455A64"]


def save_figure(fig, filename):
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGES_DIR / filename
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return path


def _pie_data(summary, top_n=6):
    """Top categories plus an 'Other' slice, so the pie chart stays readable."""
    totals = summary["Total"]
    top = totals.head(top_n)
    if len(totals) > top_n:
        top = pd.concat([top, pd.Series({"Other": totals.iloc[top_n:].sum()})])
    return top


def plot_category_totals(summary):
    data = pd.DataFrame({"Category": summary.index, "Total": summary["Total"].values})
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=data, x="Total", y="Category", color="#1565C0", ax=ax)
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{CURRENCY}{v:,.0f}" for v in data["Total"]],
                     padding=4, fontsize=9)
    ax.set_xlabel(f"Total spent ({CURRENCY})")
    ax.set_ylabel("")
    ax.set_title("Total expense by category")
    ax.set_xlim(0, data["Total"].max() * 1.15)
    return save_figure(fig, "01_category_totals.png")


def plot_expense_pie(summary):
    top = _pie_data(summary)
    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.pie(top.values, labels=top.index, autopct="%1.1f%%", startangle=90,
           colors=PALETTE[:len(top)], wedgeprops={"edgecolor": "white"})
    ax.set_title("Share of total expense by category")
    ax.axis("equal")
    return save_figure(fig, "02_expense_distribution_pie.png")


def plot_monthly_income_expense(monthly):
    x = np.arange(len(monthly))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, monthly["Income"], marker="o", color="#2E7D32", label="Income")
    ax.plot(x, monthly["Expense"], marker="o", color="#C62828", label="Expense")
    ax.set_xticks(x)
    ax.set_xticklabels(monthly.index, rotation=45)
    ax.set_ylabel(f"Amount ({CURRENCY})")
    ax.set_title("Monthly income vs expense")
    ax.grid(alpha=0.3)
    ax.legend()
    return save_figure(fig, "03_monthly_income_vs_expense.png")


def plot_monthly_spending_by_category(matrix):
    x = np.arange(len(matrix))
    bottom = np.zeros(len(matrix))
    fig, ax = plt.subplots(figsize=(11, 5.5))
    for i, category in enumerate(matrix.columns):
        values = matrix[category].values
        ax.bar(x, values, bottom=bottom, color=PALETTE[i % len(PALETTE)], label=category)
        bottom += values
    ax.set_xticks(x)
    ax.set_xticklabels(matrix.index, rotation=45)
    ax.set_ylabel(f"Amount ({CURRENCY})")
    ax.set_title("Monthly spending by category (stacked)")
    ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
    return save_figure(fig, "04_monthly_spending_by_category.png")


def plot_weekday_activity(weekday):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    sns.barplot(x=list(weekday.index), y=weekday["Transactions"].values, color="#1565C0", ax=axes[0])
    axes[0].set_title("Number of transactions by weekday")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Transactions")
    axes[0].tick_params(axis="x", rotation=45)

    sns.barplot(x=list(weekday.index), y=weekday["Total_Spent"].values, color="#EF6C00", ax=axes[1])
    axes[1].set_title(f"Total spent by weekday ({CURRENCY})")
    axes[1].set_xlabel("")
    axes[1].set_ylabel(f"Amount ({CURRENCY})")
    axes[1].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return save_figure(fig, "05_weekday_activity.png")


def plot_budget_heatmap(pivot):
    data = pivot.values
    fig, ax = plt.subplots(figsize=(12, 5))
    image = ax.imshow(data, cmap="RdYlGn_r", vmin=0, vmax=200, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=45)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            if not np.isnan(value):
                # White text on the very dark green and red cells so the numbers stay readable
                text_colour = "white" if (value < 35 or value > 150) else "black"
                ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=8, color=text_colour)
    fig.colorbar(image, ax=ax, label="% of monthly budget used")
    ax.set_title("Budget usage by category and month (100% = budget; red = overspent)")
    return save_figure(fig, "06_budget_usage_heatmap.png")


def plot_anomalies(expenses, anomalies):
    normal = expenses.drop(index=anomalies.index)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.scatter(normal["Date"], normal["Amount"], s=14, alpha=0.5, color="#1565C0", label="Normal")
    ax.scatter(anomalies["Date"], anomalies["Amount"], s=60, color="#C62828",
               label="Unusually large", zorder=3)
    for row in anomalies.itertuples():
        ax.annotate(row.Description, (row.Date, row.Amount), xytext=(6, 6),
                    textcoords="offset points", fontsize=8)
    ax.set_ylabel(f"Amount ({CURRENCY})")
    ax.set_title("Every expense over the year, with unusually large transactions highlighted")
    ax.legend()
    return save_figure(fig, "07_unusual_transactions.png")


def plot_dashboard(monthly, summary, totals, anomaly_count):
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    ax_trend, ax_category, ax_pie, ax_kpi = axes.ravel()

    x = np.arange(len(monthly))
    ax_trend.plot(x, monthly["Income"], marker="o", color="#2E7D32", label="Income")
    ax_trend.plot(x, monthly["Expense"], marker="o", color="#C62828", label="Expense")
    ax_trend.set_xticks(x)
    ax_trend.set_xticklabels(monthly.index, rotation=45, fontsize=8)
    ax_trend.set_title("Monthly income vs expense")
    ax_trend.grid(alpha=0.3)
    ax_trend.legend()

    ordered = summary["Total"].sort_values()
    ax_category.barh(ordered.index, ordered.values, color="#1565C0")
    ax_category.set_title(f"Expense by category ({CURRENCY})")

    top = _pie_data(summary)
    ax_pie.pie(top.values, labels=top.index, autopct="%1.1f%%", startangle=90,
               colors=PALETTE[:len(top)], wedgeprops={"edgecolor": "white"})
    ax_pie.set_title("Share of expense")
    ax_pie.axis("equal")

    ax_kpi.axis("off")
    ax_kpi.set_title("Key numbers", loc="left", fontsize=13)
    lines = [
        ("Total income", f"{CURRENCY}{totals['income']:,.0f}"),
        ("Total expense", f"{CURRENCY}{totals['expense']:,.0f}"),
        ("Net savings", f"{CURRENCY}{totals['savings']:,.0f}"),
        ("Savings rate", f"{totals['savings_rate_pct']:.1f}%"),
        ("Transactions", f"{totals['transactions']:,}"),
        ("Top category", f"{summary.index[0]} ({summary['Share_%'].iloc[0]:.1f}%)"),
        ("Unusually large transactions", str(anomaly_count)),
    ]
    for i, (label, value) in enumerate(lines):
        y = 0.88 - i * 0.12
        ax_kpi.text(0.02, y, label, fontsize=12, color="#444444")
        ax_kpi.text(0.98, y, value, fontsize=13, fontweight="bold", ha="right")

    fig.suptitle(f"Expense Tracker Dashboard | {totals['period_start']} to {totals['period_end']}",
                 fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    return save_figure(fig, "08_dashboard.png")
