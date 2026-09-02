"""
Step 2 — Data Cleaning
Handles missing values, duplicates, outliers, type fixes.
Saves cleaned CSV to data_cleaned.csv.
"""
import pandas as pd
import numpy as np
from config import DATA_RAW, DATA_CLEANED, TARGET

df = pd.read_csv(DATA_RAW)
print("Raw shape:", df.shape)

# ── 1. Drop duplicates ──────────────────────────────────────────────────
before = len(df)
df.drop_duplicates(inplace=True)
print(f"Duplicates removed: {before - len(df)}")

# ── 2. Handle missing values ────────────────────────────────────────────
missing = df.isnull().sum()
print("\nMissing values per column:")
print(missing[missing > 0] if missing.any() else "None")

numeric_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

for col in numeric_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].median(), inplace=True)

for col in cat_cols:
    if df[col].isnull().any():
        df[col].fillna(df[col].mode()[0], inplace=True)

# ── 3. Outlier capping (IQR method) ─────────────────────────────────────
cols_to_cap = ["Age", "Tenure", "Usage Frequency", "Support Calls",
               "Payment Delay", "Total Spend", "Last Interaction"]

for col in cols_to_cap:
    q1 = df[col].quantile(0.01)
    q99 = df[col].quantile(0.99)
    before_clip = ((df[col] < q1) | (df[col] > q99)).sum()
    df[col] = df[col].clip(q1, q99)
    if before_clip > 0:
        print(f"Clipped {before_clip} outliers in '{col}'")

# ── 4. Encode categorical features ──────────────────────────────────────
df["Gender"] = df["Gender"].map({"Male": 0, "Female": 1})

df = pd.get_dummies(df, columns=["Subscription Type", "Contract Length"],
                    drop_first=True, dtype=int)

# ── 5. Drop CustomerID (not a feature) ──────────────────────────────────
df.drop(columns=["CustomerID"], inplace=True)

# ── 6. Save ─────────────────────────────────────────────────────────────
df.to_csv(DATA_CLEANED, index=False)
print(f"\nCleaned shape: {df.shape}")
print(f"Saved to: {DATA_CLEANED}")
print("\n✅  Data cleaning complete.")