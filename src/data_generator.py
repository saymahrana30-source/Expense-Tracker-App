"""
data_generator.py
-----------------
Phase 2: creates a SYNTHETIC (simulated) expense dataset.

We simulate one financial year (April 2024 to March 2025) for one person: a
salary earner with occasional freelance income. The data is fake, but it
behaves like real spending, so the analysis works the same way.

HOW THE SIMULATION WORKS
  1. Fixed items happen every month: salary, rent, electricity, internet, mobile.
  2. Everyday items are random. Each day, the number of food orders, rides,
     shopping trips and so on is drawn from a Poisson distribution.
     Weekends and festival months (October) have higher rates, which creates trends.
  3. Amounts come from a log-normal distribution. This is a common way to model
     money: most purchases are small and a few are large.
  4. A few one-off events happen once: a trip, a course fee, a laptop, a hospital bill.
     These create the overspending and unusual-transaction cases.
  5. Real data is messy, so we add typical problems: two date formats, rupee
     signs in amounts, inconsistent category spelling, missing values and duplicates.
"""

import numpy as np
import pandas as pd

from src.config import END_DATE, INCOME_CATEGORIES, RANDOM_STATE, RAW_DATA_PATH, START_DATE

# Everyday spending: (rate on weekdays, rate on weekends, median amount in ₹, spread)
# "rate" = average number of transactions per day
DAILY_PROFILES = {
    "Food":          (0.20, 0.40, 320, 0.40),
    "Groceries":     (0.10, 0.25, 1000, 0.30),
    "Transport":     (0.45, 0.20, 150, 0.50),
    "Entertainment": (0.05, 0.30, 420, 0.50),
    "Shopping":      (0.03, 0.05, 900, 0.60),
    "Health":        (0.02, 0.02, 400, 0.60),
    "Education":     (0.02, 0.01, 700, 0.50),
}

# Seasonal multipliers by month number (festival and holiday spending)
SEASONAL_MULTIPLIER = {
    "Food":          {10: 1.5, 11: 1.3},
    "Entertainment": {10: 1.4, 12: 1.8},
    "Shopping":      {10: 3.5, 12: 2.0},
}

# Trips: (start date, number of days)
TRIPS = [("2024-06-14", 3), ("2024-12-20", 4), ("2025-02-08", 3)]

DESCRIPTIONS = {
    "Food": ["Swiggy order", "Zomato order", "Lunch at canteen", "Coffee with friends",
             "Pizza order", "Dinner out", "Street food"],
    "Groceries": ["Big Basket order", "Vegetables and fruits", "Monthly grocery run",
                  "Milk and bread", "Blinkit groceries"],
    "Transport": ["Uber ride", "Ola ride", "Metro card recharge", "Petrol",
                  "Auto rickshaw", "Bus pass"],
    "Entertainment": ["Movie tickets", "Gaming top-up", "Concert tickets", "Streaming subscription"],
    "Shopping": ["Clothes", "Shoes", "Home decor", "Electronics accessory", "Gift purchase"],
    "Health": ["Pharmacy", "Doctor consultation", "Gym membership", "Lab tests"],
    "Education": ["Books", "Stationery", "Online course"],
}


def _payment_method(rng, category):
    """Pick how the money was paid. Rent and bills usually go through net banking."""
    if category in INCOME_CATEGORIES:
        return "Net Banking"
    if category in ("Rent", "Bills"):
        return rng.choice(["Net Banking", "UPI"], p=[0.7, 0.3])
    return rng.choice(["UPI", "Card", "Cash"], p=[0.6, 0.25, 0.15])


def generate_expenses(seed=RANDOM_STATE):
    """Create the simulated transactions and return them as a DataFrame."""
    rng = np.random.default_rng(seed)
    rows = []

    def add(date, category, amount, description):
        rows.append({
            "Date": pd.Timestamp(date),
            "Category": category,
            "Description": description,
            "Amount": round(float(amount)),
            "Type": "Income" if category in INCOME_CATEGORIES else "Expense",
            "Payment_Method": _payment_method(rng, category),
        })

    # ---- 1. Fixed items every month ----------------------------------------
    for month_start in pd.date_range(START_DATE, END_DATE, freq="MS"):
        salary = 50000 if month_start < pd.Timestamp("2024-10-01") else 55000  # raise in October
        add(month_start, "Salary", salary, "Monthly salary")
        add(month_start.replace(day=5), "Rent", 14000, "Monthly house rent")

        month = month_start.month
        if month in (4, 5, 6):          # hot months, more air-conditioning
            electricity = 1700
        elif month in (12, 1, 2):
            electricity = 900
        else:
            electricity = 1100
        add(month_start.replace(day=10), "Bills", electricity + rng.normal(0, 60), "Electricity bill")
        add(month_start.replace(day=12), "Bills", 799, "Internet bill")
        add(month_start.replace(day=20), "Bills", 349, "Mobile recharge")

        if rng.random() < 0.35:         # freelance work comes in about one month in three
            day = month_start + pd.Timedelta(days=int(rng.integers(0, 28)))
            add(day, "Freelance", rng.integers(4000, 12001), "Freelance project payment")

    # ---- 2. One-off events ---------------------------------------------------
    add("2024-06-03", "Education", 8000, "Online course fee")
    add("2024-11-09", "Shopping", 18500, "Laptop purchase")
    add("2025-01-18", "Shopping", 22000, "Phone upgrade")
    add("2025-01-27", "Health", 16800, "Hospital bill")

    # ---- 3. Trips (several days of Travel spending) -------------------------
    for start, days in TRIPS:
        start = pd.Timestamp(start)
        add(start, "Travel", rng.integers(3500, 6001), "Train or flight tickets")
        for night in range(days - 1):
            add(start + pd.Timedelta(days=night), "Travel", rng.integers(2500, 4001), "Hotel stay")
        for offset in range(days):
            day = start + pd.Timedelta(days=offset)
            add(day, "Travel", rng.integers(300, 601), "Local travel")
            add(day, "Travel", rng.integers(500, 801), "Trip food")

    # ---- 4. Everyday random spending, day by day ----------------------------
    for day in pd.date_range(START_DATE, END_DATE, freq="D"):
        weekend = day.dayofweek >= 5
        for category, (rate_weekday, rate_weekend, median, spread) in DAILY_PROFILES.items():
            rate = rate_weekend if weekend else rate_weekday
            rate *= SEASONAL_MULTIPLIER.get(category, {}).get(day.month, 1.0)
            for _ in range(rng.poisson(rate)):
                amount = rng.lognormal(np.log(median), spread)
                add(day, category, amount, rng.choice(DESCRIPTIONS[category]))

    df = pd.DataFrame(rows).sort_values("Date").reset_index(drop=True)
    return add_realistic_messiness(df, rng)


def add_realistic_messiness(df, rng):
    """
    Real exports are messy. We add common problems so the cleaning step
    in preprocessing.py has real work to do.
    """
    df = df.copy()
    n = len(df)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    # Allow text values in every column that will receive messy entries
    df = df.astype({"Amount": object, "Category": object, "Type": object,
                    "Description": object, "Date": object})

    # 1. About 8% of dates written as day/month/year
    rows = rng.choice(n, size=int(0.08 * n), replace=False)
    df.loc[rows, "Date"] = pd.to_datetime(df.loc[rows, "Date"]).dt.strftime("%d/%m/%Y")

    # 2. About 3% of amounts written with a rupee sign and commas, e.g. ₹1,250
    rows = rng.choice(n, size=int(0.03 * n), replace=False)
    df.loc[rows, "Amount"] = df.loc[rows, "Amount"].map(lambda v: f"₹{int(v):,}")

    # 3. About 8% of categories with odd capitalisation or extra spaces
    rows = rng.choice(n, size=int(0.08 * n), replace=False)
    df.loc[rows, "Category"] = [
        c.lower() if rng.random() < 0.5 else f"  {c.upper()} "
        for c in df.loc[rows, "Category"]
    ]

    # 4. About 3% of types in lower or upper case
    rows = rng.choice(n, size=int(0.03 * n), replace=False)
    df.loc[rows, "Type"] = [t.lower() if rng.random() < 0.5 else t.upper()
                            for t in df.loc[rows, "Type"]]

    # 5. Missing values
    df.loc[rng.choice(n, size=int(0.01 * n), replace=False), "Amount"] = np.nan
    df.loc[rng.choice(n, size=max(1, int(0.005 * n)), replace=False), "Category"] = np.nan
    df.loc[rng.choice(n, size=3, replace=False), "Date"] = np.nan
    df.loc[rng.choice(n, size=int(0.02 * n), replace=False), "Description"] = np.nan

    # 6. Duplicate rows, as if one transaction was exported twice
    duplicates = df.sample(n=6, random_state=RANDOM_STATE)
    return pd.concat([df, duplicates], ignore_index=True)


def generate_and_save(path=RAW_DATA_PATH):
    """Generate the dataset and save it as expenses.csv."""
    df = generate_expenses()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    return df


if __name__ == "__main__":
    data = generate_and_save()
    print(f"Saved {len(data)} rows to {RAW_DATA_PATH}")
