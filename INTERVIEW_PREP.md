# Interview preparation: Expense Tracker App

Answers are based on what this project actually does and what the run produced.
Practise saying them in your own words. Do not memorise them word for word.

---

## 1. Explain your Expense Tracker App project.

I built a data science project that takes a year of personal transactions, cleans them, and turns them into insights. It answers four questions: where the money goes, whether the budget was exceeded, whether anything unusual happened, and whether the savings target was met. The data is synthetic because I do not have access to real financial records. The project runs from one command and produces charts, reports and plain-English insights.

## 2. What problem does this project solve?

Bank statements and payment apps give long lists of transactions that are hard to read. This project turns that list into a summary: spending by category, month-by-month trends, budget checks, and an alert for unusually large purchases. The people it helps are individuals managing a budget and business teams monitoring operating costs.

## 3. What type of data did you use?

Each transaction has a date, a category, a description, an amount, a type (income or expense) and a payment method. I generated a simulated financial year, April 2024 to March 2025, with about 480 transactions. I added realistic problems on purpose: dates in two formats, rupee signs in amounts, inconsistent category spelling, missing values and duplicate rows. Real data is always messy, so the cleaning step matters as much as the analysis.

## 4. What tools and libraries did you use?

- **Python** for the whole pipeline
- **pandas** to load, clean, group and summarise the data
- **NumPy** for random generation and numerical operations
- **Matplotlib** to draw the charts
- **Seaborn** for the bar charts, which look cleaner with its defaults
- **Jupyter** for the step-by-step notebook
- **Git and GitHub** to version and publish the project

## 5. What kind of analysis did you perform?

- Category analysis: total, share of spending, number of transactions, average and largest transaction
- Monthly trends: income, expense, savings and savings rate for each month
- Weekday patterns: how much is spent on each day of the week
- Budget checks: spending compared with a monthly budget for each category and month, with a 10% tolerance
- Unusual transactions: an IQR rule applied within each category, so that a large purchase is compared with similar purchases
- The 50/30/20 check: needs, wants and savings as a share of income

## 6. What visualizations did you create?

Eight charts: category totals (bar), expense share (pie), monthly income against expense (line), monthly spending by category (stacked bar), weekday activity (bars), a budget-usage heatmap, a scatter plot of every expense with unusual transactions highlighted, and a dashboard that combines the main numbers. I chose each chart for a specific question. For example, the heatmap shows which category went over budget in which month, which a single bar chart cannot show.

## 7. What insights can be generated from this project?

From the run, the project found:

- Rent is the largest expense at 37.7% of spending. The top three categories make up 59.5%.
- The savings rate was 33.4%, and the 50/30/20 targets were all met.
- January 2025 was the most expensive month, driven by a phone upgrade and a hospital bill.
- 20 category-months went over budget, and Health went over in five months.
- Weekend days cost about 1.5 times as much as weekdays per day.

The project writes these as sentences, so the text changes if the data changes.

## 8. What challenges did you face in this project?

- **Mixed date formats.** Some dates were day/month/year and others year/month/day. A single parser would turn some of them into missing values, so I parse both formats explicitly and count any that cannot be read.
- **Messy text.** The same category appeared as "food", "  FOOD " and "Food". I standardise the text, and the cleaning report counts how many values changed.
- **Type errors in pandas.** When I added rupee text such as "₹1,250" to a column that held integers, the code failed. I had to store those columns as text before inserting the messy values. This taught me to check column types before writing data.
- **Choosing an unusual-transaction rule.** A simple "more than the average" rule is distorted by the outliers themselves. The IQR rule, applied within each category, is more robust.

## 9. How can this project be improved further?

- A Streamlit dashboard so users can filter by category and date range
- Forecasting next month's spending with a time-series model
- Budget alerts, for example when a category reaches 80% of its budget
- Real data, connected through a bank or payment-app export, with a privacy policy in place
- Automated tests for the cleaning rules, so a change cannot quietly break them
- Financial goal tracking, such as saving a set amount by a set date

## 10. How would you explain this project to a non-technical person?

Imagine a notebook where you write down every rupee you spend and earn. After a year, it is hard to see the pattern. My program reads that notebook, tidies up the mistakes, adds up the totals, and draws simple pictures. It tells you in plain sentences where your money went, which months were expensive, and whether you saved enough. It also points out the one or two purchases that were much bigger than usual, so you can decide whether they were worth it.

---

## HR explanation (non-technical)

This project shows I can take messy, real-world information and turn it into a clear decision. I cleaned inconsistent records, checked the results against known rules, and presented the findings in charts and plain language. I also made it repeatable: one command reruns the whole analysis, so the numbers can be checked and updated. Those are the habits that matter in finance and business analysis roles.

## Technical explanation (for an interviewer with a data background)

The pipeline loads the raw CSV as strings, so no value is changed before it is checked. Cleaning converts dates with two explicit formats and amounts by stripping currency symbols and separators. It then standardises text, removes duplicates before and after standardising, and writes a report with the count of every fix. Feature engineering derives month, weekday, weekend flag, a signed amount and a needs/wants group. Analysis uses grouped aggregations and pivot tables. Budget checks compare each category-month total with a configured budget and a tolerance. Unusual transactions use a per-category IQR fence, Q3 + 3 × IQR, which is robust to outliers. Charts are generated from the same summary tables that feed the reports, so the visuals and the numbers cannot disagree. A notebook calls the same functions, so exploratory work and the production run use one code path.

---

## Bonus follow-up questions

**Why did you use synthetic data?**
Real financial records are private, and I did not have access to any. The simulation makes the rules explicit, so I can check whether the analysis finds the patterns I built in. The limitation is that it cannot show how real people behave, and I say so in the README.

**Why not use the mean and standard deviation to find unusual transactions?**
The mean and standard deviation are pulled by the very outliers you are looking for, so they can hide them. Quartiles are not affected by a few extreme values, which makes the IQR rule more reliable for this data.

**What would you change before using this with real money?**
I would add input validation for the bank export format, test the cleaning rules automatically, store the data in a database instead of CSV files, and make sure any personal data is handled under a clear privacy policy.
