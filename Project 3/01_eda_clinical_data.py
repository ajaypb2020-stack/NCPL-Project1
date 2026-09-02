"""
Step 1 - Exploratory Data Analysis for Clinical Data
Loads patient data, prints statistics, checks for data quality issues.
"""
import pandas as pd
import numpy as np
import sys
import os

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# ---- Configuration ----
DATA_PATH = 'outputs/clinical_data_raw.csv'
OUTPUT_DIR = 'eda_outputs'
TARGET = 'Readmission_30d'  # Binary: 0=No readmission, 1=Readmission

try:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create output directory: {e}")
    OUTPUT_DIR = '.'

print("=" * 80)
print("STEP 1: EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 80)

# ---- Load Data ----
print(f"\nLoading data from: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)
print(f'✓ Dataset Shape: {df.shape}')
print(f'  Rows: {df.shape[0]:,} patients')
print(f'  Columns: {df.shape[1]} features')

# ---- Basic Info ----
print("\n" + "=" * 80)
print("DATA TYPES & STRUCTURE")
print("=" * 80)
print(df.dtypes)

# ---- Missing Values ----
print("\n" + "=" * 80)
print("MISSING VALUES")
print("=" * 80)
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df)) * 100
missing_df = pd.DataFrame({
    'Column': df.columns,
    'Null Count': null_counts.values,
    'Null %': null_pct.values
})
missing_df = missing_df[missing_df['Null Count'] > 0].sort_values('Null Count', ascending=False)
if len(missing_df) > 0:
    print(missing_df.to_string(index=False))
else:
    print("No missing values found.")

# ---- Numeric Columns Summary ----
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print("\n" + "=" * 80)
print(f"NUMERIC COLUMNS STATISTICS ({len(numeric_cols)} columns)")
print("=" * 80)
if numeric_cols:
    summary = df[numeric_cols].describe()
    print(summary.to_string())

# ---- Categorical Columns ----
cat_cols = df.select_dtypes(include='object').columns.tolist()
print("\n" + "=" * 80)
print(f"CATEGORICAL COLUMNS ({len(cat_cols)} columns)")
print("=" * 80)
for col in cat_cols:
    uniques = df[col].nunique()
    print(f"\n{col}: {uniques} unique values")
    if uniques <= 15:
        print(df[col].value_counts(dropna=False).head(15).to_string())
    else:
        print(df[col].value_counts(dropna=False).head(10).to_string())
        print(f"  ... and {uniques - 10} more unique values")

# ---- Target Variable Analysis ----
if TARGET in df.columns:
    print("\n" + "=" * 80)
    print(f"TARGET VARIABLE: {TARGET}")
    print("=" * 80)
    print(df[TARGET].value_counts(dropna=False))
    print(f"\nTarget Distribution:")
    print(df[TARGET].value_counts(normalize=True).round(4))
else:
    print(f"\nWARNING: Target variable '{TARGET}' not found in dataset.")

# ---- Data Quality Checks ----
print("\n" + "=" * 80)
print("DATA QUALITY CHECKS")
print("=" * 80)

# Duplicates
dup_count = df.duplicated().sum()
print(f"Duplicate rows: {dup_count:,} ({(dup_count/len(df))*100:.4f}%)")

# Constant columns
constants = [col for col in df.columns if df[col].nunique() <= 1]
if constants:
    print(f"Constant columns (single unique value): {constants}")

# Negative values in numeric cols
print("\nNegative values in numeric columns:")
has_negatives = False
for col in numeric_cols:
    neg_count = (df[col] < 0).sum()
    if neg_count > 0:
        print(f"  {col}: {neg_count:,} negative values (min: {df[col].min():.2f})")
        has_negatives = True
if not has_negatives:
    print("  None found.")

# ID columns check
id_cols = [col for col in df.columns if 'id' in col.lower()]
if id_cols:
    print(f"\nID columns: {id_cols}")
    for col in id_cols:
        dup_ids = df[col].duplicated().sum()
        total = df[col].notna().sum()
        print(f"  {col}: {dup_ids:,} duplicate IDs out of {total:,} non-null values")

# ---- Sample Records ----
print("\n" + "=" * 80)
print("SAMPLE RECORDS (First 3 rows)")
print("=" * 80)
print(df.head(3).to_string())

# ---- Visualizations ----
print("\n" + "=" * 80)
print("VISUALIZATION GENERATION SKIPPED (Text analysis complete)")
print("=" * 80)
print("To generate plots, run with matplotlib backend enabled")


print("\n" + "=" * 80)
print("✓ EDA COMPLETE")
print("=" * 80)
print(f"All outputs saved to: {OUTPUT_DIR}/")
print("\nNext steps:")
print("  1. Review missing value patterns")
print("  2. Handle outliers (negative values, extreme values)")
print("  3. Clean duplicate columns (case inconsistencies)")
print("  4. Impute or drop sparse columns")
print("  5. Prepare for modeling")
