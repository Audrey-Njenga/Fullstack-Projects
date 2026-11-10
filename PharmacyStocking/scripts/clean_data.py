
import pandas as pd

# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv(
    "../data/Three_Months_Stock_Analysis.csv"
)

# ==========================================
# 2. FILTER KABATI BRANCH
# ==========================================

df["Branch"] = (
    df["Branch"]
    .astype("string")
    .str.strip()
    .str.upper()
)

df = df[df["Branch"] == "KABATI"].copy()

# ==========================================
# 3. CLEAN ITEM AND MONTH NAMES
# ==========================================

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

df = df.dropna(subset=["Item", "Month"])

df = df[df["Item"] != ""]

# ==========================================
# 4. DEFINE EXPECTED MONTHS
# ==========================================

expected_months = [
    "July",
    "August",
    "September"
]

# ==========================================
# 5. CHECK MONTHLY PRESENCE PER MEDICINE
# ==========================================

monthly_presence = (
    df.groupby("Item")["Month"]
    .apply(lambda x: sorted(set(x)))
    .reset_index()
)

# Create month presence columns
for month in expected_months:

    monthly_presence[month] = (
        monthly_presence["Month"]
        .apply(lambda x: month in x)
    )

# Count months recorded
monthly_presence["Months_Recorded"] = (
    monthly_presence[expected_months].sum(axis=1)
)

# Identify missing months
monthly_presence["Missing_Months"] = (
    monthly_presence.apply(
        lambda row: ", ".join(
            month for month in expected_months
            if not row[month]
        ),
        axis=1
    )
)

# ==========================================
# 6. CLASSIFY MEDICINES
# ==========================================

monthly_presence["Record_Status"] = (
    monthly_presence["Months_Recorded"]
    .map({
        3: "Complete - All 3 Months",
        2: "Missing 1 Month",
        1: "Missing 2 Months"
    })
)

# ==========================================
# 7. SEPARATE COMPLETE AND INCOMPLETE RECORDS
# ==========================================

complete_records = monthly_presence[
    monthly_presence["Months_Recorded"] == 3
].copy()

incomplete_records = monthly_presence[
    monthly_presence["Months_Recorded"] < 3
].copy()

# Sort incomplete records
incomplete_records = incomplete_records.sort_values(
    ["Months_Recorded", "Item"],
    ascending=[True, True]
)

# ==========================================
# 8. SUMMARY BY MONTH
# ==========================================

missing_by_month = pd.DataFrame({
    "Month": expected_months,
    "Medicines_Missing": [
        (~monthly_presence[month]).sum()
        for month in expected_months
    ]
})

# ==========================================
# 9. EXPORT RESULTS
# ==========================================

with pd.ExcelWriter(
    "Kabati_Medicine_Monthly_Completeness.xlsx",
    engine="openpyxl"
) as writer:

    monthly_presence.drop(
        columns=["Month"]
    ).to_excel(
        writer,
        sheet_name="All Medicines",
        index=False
    )

    incomplete_records.drop(
        columns=["Month"]
    ).to_excel(
        writer,
        sheet_name="Missing Records",
        index=False
    )

    complete_records.drop(
        columns=["Month"]
    ).to_excel(
        writer,
        sheet_name="Complete Records",
        index=False
    )

    missing_by_month.to_excel(
        writer,
        sheet_name="Monthly Summary",
        index=False
    )

# ==========================================
# 10. DISPLAY RESULTS
# ==========================================

print("\n====================================")
print("KABATI MEDICINE RECORD COMPLETENESS")
print("JULY - SEPTEMBER")
print("====================================")

print("\nTotal unique medicines:",
      len(monthly_presence))

print("\nMedicines recorded in all 3 months:",
      len(complete_records))

print("\nMedicines missing at least one month:",
      len(incomplete_records))

print("\nMISSING MEDICINE RECORDS:")
print(
    incomplete_records[
        ["Item", "Months_Recorded",
         "Missing_Months", "Record_Status"]
    ].to_string(index=False)
)

print("\nMISSING RECORDS BY MONTH:")
print(missing_by_month.to_string(index=False))

print("\nResults saved to:")
print("Kabati_Medicine_Monthly_Completeness.xlsx")
