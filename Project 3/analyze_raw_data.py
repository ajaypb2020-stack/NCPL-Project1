"""
Fast raw data analysis for clinical_data_raw.csv
"""
import pandas as pd
import numpy as np
from pathlib import Path

csv_path = Path("C:/Users/swarn/Bootcamp-P3/outputs/clinical_data_raw.csv")
print(f"Loading {csv_path.name}...\n")
print("=" * 100)

# Load with chunking to handle large file
df = pd.read_csv(csv_path)

rows, cols = df.shape
file_size_mb = csv_path.stat().st_size / (1024**2)

print(f"📊 DATASET OVERVIEW")
print(f"  Rows: {rows:,}")
print(f"  Columns: {cols}")
print(f"  File Size: {file_size_mb:.2f} MB\n")

print(f"📋 COLUMNS")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col:30s} {str(df[col].dtype):10s}")

print(f"\n❌ MISSING DATA (columns with nulls)")
null_info = df.isnull().sum()
null_pct = (null_info / rows) * 100
has_nulls = null_info[null_info > 0]
if len(has_nulls) > 0:
    for col in has_nulls.index:
        print(f"  {col:30s}: {has_nulls[col]:>8,} ({null_pct[col]:>6.2f}%)")
else:
    print("  No missing values")

print(f"\n🔢 NUMERIC SUMMARY (first 5 numeric columns)")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()[:5]
if numeric_cols:
    print(df[numeric_cols].describe().T.to_string())

print(f"\n🏷️ CATEGORICAL COLUMNS")
cat_cols = df.select_dtypes(include='object').columns.tolist()
for col in cat_cols[:10]:
    uniques = df[col].nunique()
    print(f"  {col:30s}: {uniques:>6,} unique values")

print(f"\n📖 SAMPLE ROW (Row 0)")
print(df.iloc[0].to_string())

print(f"\n📈 FULL COLUMN SUMMARY")
summary_rows = []
for col in df.columns:
    summary_rows.append({
        'Column': col,
        'Dtype': str(df[col].dtype),
        'Nulls': df[col].isnull().sum(),
        'Uniques': df[col].nunique(),
        'Non-null %': f"{((df[col].notna().sum() / rows) * 100):.1f}%"
    })
summary_df = pd.DataFrame(summary_rows)
print(summary_df.to_string(index=False))

print("\n" + "=" * 100)
print("✨ Analysis complete.")
