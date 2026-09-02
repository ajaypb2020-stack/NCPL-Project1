"""
Step 2 - Data Cleaning Pipeline
Handles missing values, removes outliers, validates data, and prepares for modeling.
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("STEP 2: DATA CLEANING & PREPARATION")
print("=" * 80)

# ---- Configuration ----
DATA_RAW = 'outputs/clinical_data_raw.csv'
DATA_CLEANED = 'data_cleaned.csv'
OUTPUT_DIR = 'outputs'

# ---- Load Raw Data ----
print(f"\nLoading raw data: {DATA_RAW}")
df = pd.read_csv(DATA_RAW)
print(f"✓ Loaded: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ---- Phase 1: Drop Redundant & Unusable Columns ----
print("\n" + "=" * 80)
print("PHASE 1: Column Reduction")
print("=" * 80)

# Completely null columns
drop_cols_null = ['Extra_Col_1', 'Extra_Col_2', 'Notes', 'unnamed_0']
# Redundant columns (lowercase versions)
drop_cols_dup = ['age', 'gender', 'drug_name', 'Weight_lbs']
# High missing rate (> 25%)
drop_cols_sparse = ['Alcohol_Use', 'Admission_Date']

all_drop_cols = drop_cols_null + drop_cols_dup + drop_cols_sparse
existing_drop = [col for col in all_drop_cols if col in df.columns]

print(f"\nDropping {len(existing_drop)} columns:")
for col in existing_drop:
    null_pct = (df[col].isnull().sum() / len(df)) * 100
    print(f"  - {col:20s} ({null_pct:6.2f}% null)")

df = df.drop(columns=existing_drop)
print(f"✓ Reduced to: {df.shape[0]:,} rows × {df.shape[1]} columns")

# ---- Phase 2: Remove Rows with Missing Target ----
print("\n" + "=" * 80)
print("PHASE 2: Remove Missing Target Values")
print("=" * 80)

TARGET = 'Readmission_30d'
initial_rows = len(df)
df = df.dropna(subset=[TARGET])
rows_dropped = initial_rows - len(df)
print(f"Removed {rows_dropped:,} rows with missing target")
print(f"✓ Remaining: {len(df):,} rows")

# ---- Phase 3: Outlier Removal ----
print("\n" + "=" * 80)
print("PHASE 3: Outlier & Invalid Value Removal")
print("=" * 80)

# Age validation
print(f"\nAge: Before cleaning: {len(df)} rows")
age_before = len(df)
df = df[(df['Age'] >= 18) & (df['Age'] <= 120)]
age_removed = age_before - len(df)
print(f"  Removed {age_removed:,} rows with Age < 18 or Age > 120")
print(f"  Remaining: {len(df)} rows")

# Weight validation
print(f"\nWeight_kg: Before cleaning: {len(df)} rows")
weight_before = len(df)
df = df[(df['Weight_kg'] >= 30) & (df['Weight_kg'] <= 200)]
weight_removed = weight_before - len(df)
print(f"  Removed {weight_removed:,} rows with Weight < 30 or > 200 kg")
print(f"  Remaining: {len(df)} rows")

# Heart rate validation
print(f"\nHeart_Rate: Before cleaning: {len(df)} rows")
hr_before = len(df)
df = df[(df['Heart_Rate'] >= 40) & (df['Heart_Rate'] <= 160)]
hr_removed = hr_before - len(df)
print(f"  Removed {hr_removed:,} rows with Heart_Rate < 40 or > 160")
print(f"  Remaining: {len(df)} rows")

# Temperature validation
print(f"\nTemperature_F: Before cleaning: {len(df)} rows")
temp_before = len(df)
df = df[(df['Temperature_F'] >= 95) & (df['Temperature_F'] <= 105)]
temp_removed = temp_before - len(df)
print(f"  Removed {temp_removed:,} rows with Temperature < 95 or > 105°F")
print(f"  Remaining: {len(df)} rows")

print(f"\n✓ Total rows after outlier removal: {len(df):,}")

# ---- Phase 4: Data Type Validation ----
print("\n" + "=" * 80)
print("PHASE 4: Data Type Validation")
print("=" * 80)

# Ensure numeric columns are numeric
numeric_required = ['Age', 'Weight_kg', 'Height_cm', 'BMI', 'Systolic_BP', 
                   'Diastolic_BP', 'Heart_Rate', 'Temperature_F',
                   'Hemoglobin', 'WBC_Count', 'ALT_Enzyme', 'AST_Enzyme',
                   'Creatinine', 'eGFR', 'HbA1c', 'Total_Cholesterol',
                   'Concurrent_Drugs', TARGET]

for col in numeric_required:
    if col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"✓ Converted {col} to numeric")
            except:
                print(f"⚠ Could not convert {col} to numeric")

# ---- Phase 5: Missing Value Imputation ----
print("\n" + "=" * 80)
print("PHASE 5: Missing Value Imputation")
print("=" * 80)

# Numeric imputation (median)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
numeric_cols = [col for col in numeric_cols if col != TARGET]

print(f"\nImputing {len(numeric_cols)} numeric columns with median:")
for col in numeric_cols:
    null_count = df[col].isnull().sum()
    if null_count > 0:
        median_val = df[col].median()
        df[col].fillna(median_val, inplace=True)
        print(f"  {col:25s}: {null_count:>6,} values → {median_val:.2f}")

# Categorical imputation (mode or 'Unknown')
cat_cols = df.select_dtypes(include='object').columns.tolist()
print(f"\nImputing {len(cat_cols)} categorical columns:")
for col in cat_cols:
    null_count = df[col].isnull().sum()
    if null_count > 0:
        mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
        df[col].fillna(mode_val, inplace=True)
        print(f"  {col:25s}: {null_count:>6,} values → '{mode_val}'")

print(f"\n✓ Missing values after imputation: {df.isnull().sum().sum()}")

# ---- Phase 6: Feature Cleaning ----
print("\n" + "=" * 80)
print("PHASE 6: Feature Cleaning & Standardization")
print("=" * 80)

# Standardize Gender values
print("\nStandardizing Gender:")
print(f"  Before: {df['Gender'].nunique()} unique values")
df['Gender'] = df['Gender'].str.strip().str.title()
gender_valid = {'Male', 'Female', 'Other', 'Unknown'}
df['Gender'] = df['Gender'].apply(lambda x: x if x in gender_valid else 'Other')
print(f"  After: {df['Gender'].nunique()} unique values - {df['Gender'].unique().tolist()}")

# Parse blood_pressure if string format exists
if 'blood_pressure' in df.columns and df['blood_pressure'].dtype == 'object':
    print("\nParsing blood_pressure (string to numeric):")
    df['blood_pressure'] = pd.to_numeric(df['blood_pressure'], errors='coerce')
    df['blood_pressure'].fillna(df['blood_pressure'].median(), inplace=True)

# Standardize Diagnosis
if 'Diagnosis' in df.columns:
    print("\nStandardizing Diagnosis:")
    print(f"  Unique values before: {df['Diagnosis'].nunique()}")
    df['Diagnosis'] = df['Diagnosis'].str.lower().str.strip()
    print(f"  Unique values after: {df['Diagnosis'].nunique()}")

# Standardize Treatment_Outcome
if 'Treatment_Outcome' in df.columns:
    print("\nStandardizing Treatment_Outcome:")
    print(f"  Before: {df['Treatment_Outcome'].unique().tolist()}")
    df['Treatment_Outcome'] = df['Treatment_Outcome'].str.lower().str.strip()
    print(f"  After: {df['Treatment_Outcome'].unique().tolist()}")

# ---- Phase 7: Summary Stats ----
print("\n" + "=" * 80)
print("PHASE 7: Data Quality Summary")
print("=" * 80)

print(f"\n✓ Final Dataset Shape: {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"✓ Missing Values: {df.isnull().sum().sum()} (all imputed)")
print(f"✓ Duplicate Rows: {df.duplicated().sum():,}")

# Target balance
print(f"\nTarget Distribution ({TARGET}):")
print(df[TARGET].value_counts().to_string())
print("\nTarget % Distribution:")
print(df[TARGET].value_counts(normalize=True).round(4).to_string())

# Data types
print(f"\nData Types:")
print(df.dtypes.value_counts().to_string())

# ---- Save Cleaned Data ----
print("\n" + "=" * 80)
print("SAVING CLEANED DATA")
print("=" * 80)

output_path = f"{OUTPUT_DIR}/{DATA_CLEANED}"
df.to_csv(output_path, index=False)
print(f"\n✓ Saved to: {output_path}")
print(f"✓ File size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

# Save cleaning report
print("\n" + "=" * 80)
print("✓ DATA CLEANING COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("  1. Run feature engineering script")
print("  2. Build models (Decision Tree, Random Forest, XGBoost)")
print("  3. Evaluate and compare models")
