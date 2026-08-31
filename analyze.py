import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('customer_churn_dataset-testing-master.csv')

rows, cols = df.shape
print('=== Basic Info ===')
print(f'Rows: {rows}')
print(f'Columns: {cols}')

print('\n=== Columns, Inferred Dtypes, Nulls, Blanks, Uniques ===')
# Nulls
null_counts = df.isnull().sum()
# Blanks (whitespaces/empty strings in object columns)
def count_blanks(series):
    if series.dtype == 'object':
        return series.astype(str).str.strip().eq('').sum()
    return 0

blank_counts = df.apply(count_blanks)

summary_df = pd.DataFrame({
    'Dtype': df.dtypes,
    'Nulls': null_counts,
    'Null %': (null_counts / rows) * 100,
    'Blanks': blank_counts,
    'Blank %': (blank_counts / rows) * 100,
    'Uniques': df.nunique()
})
print(summary_df.to_string())

# Duplicate rows
dup_count = df.duplicated().sum()
print(f'\nDuplicate rows: {dup_count} ({(dup_count/rows)*100:.4f}%)')

# Numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
print('\n=== Numeric Summary Statistics ===')
pd.set_option('display.float_format', lambda x: '%.4f' % x)
print(df[numeric_cols].describe().to_string())

# Categorical column value counts for low cardinality (< 15 uniques)
print('\n=== Low Cardinality Column Value Counts ===')
for col in df.columns:
    uniques = df[col].nunique()
    if uniques <= 15:
        print(f'\nValue counts for column "{col}" (Unique values: {uniques}):')
        print(df[col].value_counts(dropna=False).to_string())

# Suspicious or constant columns
print('\n=== Suspicious/Constant values ===')
# Constant columns
constants = [col for col in df.columns if df[col].nunique() <= 1]
print(f'Constant Columns: {constants}')

# Negative value checks
print('Negative values check:')
for col in numeric_cols:
    neg_count = (df[col] < 0).sum()
    print(f'  {col}: {neg_count} negative values')

if 'CustomerID' in df.columns:
    dup_ids = df['CustomerID'].duplicated().sum()
    print(f'Duplicate CustomerID count: {dup_ids}')

print(f'Age Range: {df["Age"].min()} to {df["Age"].max()}')
