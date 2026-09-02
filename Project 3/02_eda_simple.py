"""
EDA Script - Writes output to file for inspection
"""
import pandas as pd
import numpy as np
import sys
import os

# Redirect output to file
output_file = open('eda_analysis.txt', 'w')

def log(msg):
    output_file.write(msg + '\n')
    output_file.flush()
    print(msg)  # Also print to console

# ---- Load Data ----
data_path = 'outputs/clinical_data_raw.csv'
log("=" * 80)
log("STEP 1: EXPLORATORY DATA ANALYSIS (EDA)")
log("=" * 80)
log(f"\nLoading data from: {data_path}")

try:
    df = pd.read_csv(data_path)
    log(f'✓ Dataset Shape: {df.shape}')
    log(f'  Rows: {df.shape[0]:,} patients')
    log(f'  Columns: {df.shape[1]} features')
except Exception as e:
    log(f'✗ ERROR loading data: {e}')
    output_file.close()
    sys.exit(1)

# ---- Data Types ----
log("\n" + "=" * 80)
log("DATA TYPES & STRUCTURE")
log("=" * 80)
log(str(df.dtypes))

# ---- Missing Values ----
log("\n" + "=" * 80)
log("MISSING VALUES")
log("=" * 80)
null_counts = df.isnull().sum()
null_pct = (null_counts / len(df)) * 100
missing_df = pd.DataFrame({
    'Column': df.columns,
    'Null Count': null_counts.values,
    'Null %': null_pct.values
})
missing_df = missing_df[missing_df['Null Count'] > 0].sort_values('Null Count', ascending=False)
if len(missing_df) > 0:
    log(missing_df.to_string(index=False))
else:
    log("No missing values found.")

# ---- Numeric Summary ----
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
log("\n" + "=" * 80)
log(f"NUMERIC COLUMNS ({len(numeric_cols)} columns)")
log("=" * 80)
if numeric_cols:
    log(df[numeric_cols].describe().to_string())

# ---- Categorical Analysis ----
cat_cols = df.select_dtypes(include='object').columns.tolist()
log("\n" + "=" * 80)
log(f"CATEGORICAL COLUMNS ({len(cat_cols)} columns)")
log("=" * 80)
for col in cat_cols[:5]:  # Only first 5 to keep output manageable
    uniques = df[col].nunique()
    log(f"\n{col}: {uniques} unique values")
    if uniques <= 20:
        log(df[col].value_counts(dropna=False).head(20).to_string())
    else:
        log(df[col].value_counts(dropna=False).head(10).to_string())

# ---- Target Variable ----
TARGET = 'Readmission_30d'
if TARGET in df.columns:
    log("\n" + "=" * 80)
    log(f"TARGET VARIABLE: {TARGET}")
    log("=" * 80)
    log(df[TARGET].value_counts(dropna=False).to_string())
    log("\nTarget Distribution (%):")
    log(df[TARGET].value_counts(normalize=True).round(4).to_string())

# ---- Data Quality ----
log("\n" + "=" * 80)
log("DATA QUALITY CHECKS")
log("=" * 80)
dup_count = df.duplicated().sum()
log(f"Duplicate rows: {dup_count:,} ({(dup_count/len(df))*100:.4f}%)")

# Negative values
log("\nNegative values in numeric columns:")
has_negatives = False
for col in numeric_cols:
    neg_count = (df[col] < 0).sum()
    if neg_count > 0:
        log(f"  {col}: {neg_count:,} negative values (min: {df[col].min():.2f})")
        has_negatives = True
if not has_negatives:
    log("  None found.")

log("\n" + "=" * 80)
log("✓ EDA COMPLETE")
log("=" * 80)

output_file.close()
print("\n✓ Output saved to: eda_analysis.txt")
