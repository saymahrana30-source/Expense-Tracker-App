"""
config.py
---------
Every path and setting used by the project lives here.
Change a value in this file and the rest of the project follows.
"""

from pathlib import Path

# The project root is the folder that contains main.py (this file is in src/).
ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "expenses.csv"
PROCESSED_DATA_PATH = DATA_DIR / "processed" / "cleaned_expenses.csv"

OUTPUTS_DIR = ROOT_DIR / "outputs"
IMAGES_DIR = ROOT_DIR / "images"

# One simulated financial year (April to March, the Indian financial year)
START_DATE = "2024-04-01"
END_DATE = "2025-03-31"
RANDOM_STATE = 42          # fixed seed so every run gives the same data
CURRENCY = "₹"

INCOME_CATEGORIES = ["Salary", "Freelance"]

# Needs are essentials, wants are optional. Used for the 50/30/20 budgeting check.
NEEDS = {"Rent", "Bills", "Groceries", "Transport", "Health", "Education"}
WANTS = {"Food", "Travel", "Entertainment", "Shopping"}

# Monthly budget for each expense category, in rupees
MONTHLY_BUDGETS = {
    "Rent": 14000,
    "Bills": 3000,
    "Groceries": 5000,
    "Food": 3000,
    "Transport": 2500,
    "Travel": 2000,
    "Entertainment": 2000,
    "Shopping": 3000,
    "Health": 1000,
    "Education": 1500,
}

OVERSPEND_TOLERANCE = 0.10      # flag a category if spending is more than 10% over budget
ANOMALY_IQR_MULTIPLIER = 3.0    # flag a transaction above Q3 + 3 x IQR within its category
MIN_ROWS_FOR_ANOMALY_CHECK = 8  # skip categories with too few transactions to judge
