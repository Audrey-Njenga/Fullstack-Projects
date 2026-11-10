
import pandas as pd

# ==========================================
# 1. JULY DATA - SEPARATE BRANCH SHEETS
# ==========================================

july_sheets = pd.read_excel(
    "data/july.xlsx",
    sheet_name=None,
    header=0
)

july_data = []

july_mapping = {
    "NAME": "Item",
    "INITIAL": "Initial Stock",
    "IN": "Stock In",
    "BP": "Buying Price",
    "JULY": "Stock In Cost",
    "TOTAL BP": "Total Buying Cost",
    "SOLD": "Stock Sold",
    "SP": "Selling Price",
    "TOTAL SALES": "Total Sales",
    "BAL": "Stock Balance",
    "STOCK VALUE": "Stock Value"
}

for branch, df in july_sheets.items():

    # Clean column headers
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.upper()
    )

    # Standardise column names
    df = df.rename(columns=july_mapping)

    # Add branch and month
    df["Branch"] = branch
    df["Month"] = "July"

    july_data.append(df)

july = pd.concat(july_data, ignore_index=True)


# ==========================================
# 2. AUGUST DATA - ALL BRANCHES SHEET
# ==========================================

august = pd.read_excel(
    "data/august.xlsx",
    sheet_name="All Branches",
    header=0
)

# Clean column headers
august.columns = (
    august.columns.astype(str)
    .str.strip()
)

august_mapping = {
    "Branch": "Branch",
    "Category": "Category",
    "Item Name": "Item",
    "Initial Stock": "Initial Stock",
    "Stock In": "Stock In",
    "Buying Price": "Buying Price",
    "Stock Sold": "Stock Sold",
    "Selling Price": "Selling Price",
    "Stock In Cost": "Stock In Cost",
    "Total Buying Cost (Initial+In)": "Total Buying Cost",
    "Total Sales": "Total Sales",
    "Stock Balance": "Stock Balance",
    "Balance Value @ Buying": "Stock Value"
}

august = august.rename(columns=august_mapping)

# Add month
august["Month"] = "August"


# ==========================================
# 3. SEPTEMBER DATA - MERGED STOCK SHEET
# ==========================================

september = pd.read_excel(
    "data/sept.xlsx",
    sheet_name="Merged Stock",
    header=3
)

# Clean column headers
september.columns = (
    september.columns.astype(str)
    .str.strip()
)

september_mapping = {
    "Branch": "Branch",
    "Category": "Category",
    "Item Name": "Item",
    "Initial Stock": "Initial Stock",
    "Stock In": "Stock In",
    "Buying Price": "Buying Price",
    "Stock Sold": "Stock Sold",
    "Selling Price": "Selling Price",
    "Stock In Cost": "Stock In Cost",
    "Total Buying Cost (Initial+In)": "Total Buying Cost",
    "Total Sales": "Total Sales",
    "Stock Balance": "Stock Balance",
    "Balance Value @ Buying": "Stock Value"
}

september = september.rename(columns=september_mapping)

# Add month
september["Month"] = "September"


# ==========================================
# 4. STANDARDISE ALL COLUMNS
# ==========================================

common_columns = [
    "Month",
    "Branch",
    "Category",
    "Item",
    "Initial Stock",
    "Stock In",
    "Buying Price",
    "Stock In Cost",
    "Total Buying Cost",
    "Stock Sold",
    "Selling Price",
    "Total Sales",
    "Stock Balance",
    "Stock Value"
]

july = july.reindex(columns=common_columns)
august = august.reindex(columns=common_columns)
september = september.reindex(columns=common_columns)


# ==========================================
# 5. COMBINE ALL THREE MONTHS
# ==========================================

combined = pd.concat(
    [july, august, september],
    ignore_index=True
)


# ==========================================
# FILTER KABATI BRANCH ONLY
# ==========================================

combined["Branch"] = (
    combined["Branch"]
    .astype("string")
    .str.strip()
)

combined = combined[
    combined["Branch"].str.upper() == "KABATI"
].copy()

# ==========================================
# 6. CLEAN ITEM, CATEGORY AND BRANCH NAMES
# ==========================================

# Clean item names
combined["Item"] = (
    combined["Item"]
    .astype("string")
    .str.strip()
    .str.upper()
)

# Clean branch names
combined["Branch"] = (
    combined["Branch"]
    .astype("string")
    .str.strip()
)

# Clean category names
combined["Category"] = (
    combined["Category"]
    .astype("string")
    .str.strip()
)


# ==========================================
# 7. REMOVE BLANK ITEM NAMES
# ==========================================

combined = combined.dropna(subset=["Item"])

combined = combined[
    combined["Item"] != ""
]

combined = combined.reset_index(drop=True)


# ==========================================
# 8. EXPORT TO CSV
# ==========================================

combined.to_csv(
    "Three_Months_Stock_Analysis.csv",
    index=False,
    encoding="utf-8-sig"
)


# ==========================================
# 9. DISPLAY SUMMARY
# ==========================================

print("\nSuccessfully combined July, August and September!")

print("\nTotal records:", len(combined))

print("\nRecords per month:")
print(combined["Month"].value_counts())

print("\nRecords per branch:")
print(combined.groupby("Branch").size())

print("\nRecords per category:")
print(combined["Category"].value_counts(dropna=False))

print("\nCSV file successfully saved as:")
print("Three_Months_Stock_Analysis.csv")
