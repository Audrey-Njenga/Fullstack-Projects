
import pandas as pd
import numpy as np

# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv(
    "../data/Three_Months_Stock_Analysis.csv"
)

# Filter Kabati branch
df["Branch"] = (
    df["Branch"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df = df[df["Branch"] == "KABATI"].copy()

# Clean item names
df["Item"] = (
    df["Item"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df["Month"] = (
    df["Month"]
    .astype("string")
    .str.strip()
    .str.title()
)

# Convert sales to numeric
df["Stock Sold"] = pd.to_numeric(
    df["Stock Sold"],
    errors="coerce"
)

# ==========================================
# 2. IDENTIFY MEDICINES IN ALL 3 MONTHS
# ==========================================

months = ["July", "August", "September"]

# Identify unique medicine-month combinations
presence = (
    df.groupby("Item")["Month"]
    .nunique()
)

complete_items = presence[
    presence == 3
].index

# Keep only the 365 complete medicines
complete_df = df[
    df["Item"].isin(complete_items)
].copy()

print("Complete medicines:", len(complete_items))

# ==========================================
# 3. PREPARE MONTHLY SALES DATA
# ==========================================

# Missing sales values within an existing record
# are treated as zero for this initial analysis.
complete_df["Stock Sold"] = (
    complete_df["Stock Sold"].fillna(0)
)

# Aggregate duplicate item entries within each month
sales = (
    complete_df
    .groupby(["Item", "Month"])["Stock Sold"]
    .sum()
    .unstack(fill_value=0)
)

# Ensure correct month order
sales = sales.reindex(
    columns=months,
    fill_value=0
)

sales = sales.reset_index()

# ==========================================
# 4. METHOD 1: THREE-MONTH AVERAGE
# ==========================================

sales["Average_Forecast"] = (
    sales[months].mean(axis=1)
)

# ==========================================
# 5. METHOD 2: WEIGHTED AVERAGE
# ==========================================

sales["Weighted_Forecast"] = (
    sales["July"] * 0.20 +
    sales["August"] * 0.30 +
    sales["September"] * 0.50
)

# ==========================================
# 6. METHOD 3: LINEAR TREND FORECAST
# ==========================================

def calculate_trend(row):

    historical_sales = np.array([
        row["July"],
        row["August"],
        row["September"]
    ])

    # Fit a straight-line trend
    x = np.array([1, 2, 3])

    slope, intercept = np.polyfit(
        x,
        historical_sales,
        1
    )

    # Predict month 4 (October)
    forecast = slope * 4 + intercept

    return max(0, forecast)


sales["Trend_Forecast"] = sales.apply(
    calculate_trend,
    axis=1
)

# ==========================================
# 7. SELECT RECOMMENDED FORECAST
# ==========================================

# Use weighted average as the initial baseline
sales["October_Forecast"] = (
    sales["Weighted_Forecast"]
)

# Round to whole units
sales["October_Forecast"] = (
    sales["October_Forecast"].round().astype(int)
)

# ==========================================
# 8. ANALYSE SALES DIRECTION
# ==========================================

def sales_direction(row):

    july = row["July"]
    august = row["August"]
    september = row["September"]

    if july < august < september:
        return "Consistently Increasing"

    elif july > august > september:
        return "Consistently Decreasing"

    elif july == august == september:
        return "Stable"

    elif september > july:
        return "Generally Increasing"

    elif september < july:
        return "Generally Decreasing"

    else:
        return "Fluctuating"


sales["Sales_Trend"] = sales.apply(
    sales_direction,
    axis=1
)

# ==========================================
# 9. CLASSIFY OCTOBER DEMAND
# ==========================================

def demand_category(row):

    avg = row["Average_Forecast"]
    forecast = row["October_Forecast"]

    if forecast == 0:
        return "No Forecasted Sales"

    elif forecast >= 1.5 * avg:
        return "High Demand"

    elif forecast <= 0.5 * avg:
        return "Low Demand"

    else:
        return "Normal Demand"


sales["Demand_Category"] = sales.apply(
    demand_category,
    axis=1
)

# ==========================================
# 10. RANK MEDICINES BY OCTOBER FORECAST
# ==========================================

sales = sales.sort_values(
    "October_Forecast",
    ascending=False
)

sales["Demand_Rank"] = range(
    1,
    len(sales) + 1
)

# ==========================================
# 11. EXPORT FORECAST
# ==========================================

sales.to_csv(
    "Kabati_October_Sales_Forecast.csv",
    index=False,
    encoding="utf-8-sig"
)

# ==========================================
# 12. DISPLAY SUMMARY
# ==========================================

print("\n====================================")
print("KABATI OCTOBER SALES FORECAST")
print("====================================")

print("\nTotal medicines forecast:",
      len(sales))

print("\nTotal July sales:",
      sales["July"].sum())

print("Total August sales:",
      sales["August"].sum())

print("Total September sales:",
      sales["September"].sum())

print("\nForecast October total units:",
      sales["October_Forecast"].sum())

print("\nTop 20 forecasted medicines:")
print(
    sales[
        ["Item", "July", "August", "September",
         "October_Forecast", "Sales_Trend"]
    ].head(20).to_string(index=False)
)

print("\nDemand categories:")
print(
    sales["Demand_Category"].value_counts()
)

print("\nForecast saved as:")
print("Kabati_October_Sales_Forecast.csv")
