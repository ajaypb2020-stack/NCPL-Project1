"""
Step 1 - Exploratory Data Analysis for Clinical Data
Loads patient data, prints statistics, checks for issues.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("STEP 1: EXPLORATORY DATA ANALYSIS (EDA)")
print("=" * 80)

# ---- Configuration ----
DATA_PATH = 'outputs/clinical_data_raw.csv'
OUTPUT_DIR = 'outputs'
TARGET = 'Readmission_30d'  # 1=Readmitted, 0=Not readmitted
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- Load Data ----
print(f'\nLoading data from: {DATA_PATH}')
if not os.path.exists(DATA_PATH):
    print(f'ERROR: File not found: {DATA_PATH}')
    sys.exit(1)

try:
    df = pd.read_csv(DATA_PATH)
    print(f'✓ Successfully loaded')
except Exception as e:
    print(f'ERROR loading file: {e}')
    sys.exit(1)

print(f'\nDataset Shape: {df.shape}')
print(f'  Rows: {df.shape[0]:,} patients')
print(f'  Columns: {df.shape[1]} features')

# ---- Basic Statistics ----
print('\n' + '=' * 80)
print('COLUMN TYPES')
print('=' * 80)
print(df.dtypes)

print('\n' + '=' * 80)
print('FIRST 5 ROWS')
print('=' * 80)
print(df.head())

print('\n' + '=' * 80)
print('DESCRIPTIVE STATISTICS')
print('=' * 80)
print(df.describe())

print('\n' + '=' * 80)
print('MISSING VALUES')
print('=' * 80)
null_counts = df.isnull().sum()
if null_counts.sum() > 0:
    null_df = pd.DataFrame({
        'Column': null_counts.index,
        'Null_Count': null_counts.values,
        'Null_%': (null_counts.values / len(df) * 100).round(2)
    })
    null_df = null_df[null_df['Null_Count'] > 0].sort_values('Null_Count', ascending=False)
    print(null_df.to_string(index=False))
else:
    print("No missing values found.")

# ---- Target Variable Balance ----
print('\n' + '=' * 80)
print('TARGET VARIABLE DISTRIBUTION')
print('=' * 80)
if TARGET in df.columns:
    print(f'\nTarget: {TARGET}')
    print('\nValue Counts:')
    print(df[TARGET].value_counts().sort_index())
    print('\nPercentage Distribution:')
    print(df[TARGET].value_counts(normalize=True).sort_index().round(4) * 100)
else:
    print(f'WARNING: Target column "{TARGET}" not found in dataset')
    print(f'Available columns: {list(df.columns)}')

# ---- Distribution Plots ----
print('\n' + '=' * 80)
print('GENERATING DISTRIBUTION PLOTS')
print('=' * 80)

try:
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['patient_id', 'Patient_ID', 'unnamed_0', 'Unnamed: 0']]
    
    if len(numeric_cols) > 0:
        print(f'Creating histograms for {len(numeric_cols)} numeric columns...')
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, (ax, col) in enumerate(zip(axes, numeric_cols[:9])):
            try:
                sns.histplot(df[col], kde=True, ax=ax, color='teal', bins=30)
                ax.set_title(f'Distribution of {col}')
                ax.set_xlabel(col)
                ax.set_ylabel('Frequency')
            except Exception as e:
                ax.text(0.5, 0.5, f'Error plotting {col}\n{str(e)}', 
                        ha='center', va='center', transform=ax.transAxes)
        
        # Hide unused subplots
        for i in range(len(numeric_cols), 9):
            axes[i].axis('off')
        
        plt.tight_layout()
        output_file = f'{OUTPUT_DIR}/step1_clinical_distributions.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ Saved distribution plots to: {output_file}')
    else:
        print('No numeric columns found for distribution plots')
        
except Exception as e:
    print(f'ERROR creating distribution plots: {e}')
    import traceback
    traceback.print_exc()

# ---- Correlation Heatmap ----
print('\n' + '=' * 80)
print('GENERATING CORRELATION HEATMAP')
print('=' * 80)

try:
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    numeric_cols = [c for c in numeric_cols if c not in ['patient_id', 'Patient_ID', 'unnamed_0', 'Unnamed: 0']]
    
    if len(numeric_cols) > 1:
        print(f'Computing correlation for {len(numeric_cols)} numeric columns...')
        plt.figure(figsize=(14, 10))
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt='.2f', 
                   square=True, linewidths=0.5, cbar_kws={'label': 'Correlation'})
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        output_file = f'{OUTPUT_DIR}/step1_correlation_matrix.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f'✓ Saved correlation heatmap to: {output_file}')
    else:
        print('Not enough numeric columns for correlation matrix')
        
except Exception as e:
    print(f'ERROR creating correlation heatmap: {e}')
    import traceback
    traceback.print_exc()

# ---- Data Quality Summary ----
print('\n' + '=' * 80)
print('DATA QUALITY SUMMARY')
print('=' * 80)

print(f'\nDuplicate Rows: {df.duplicated().sum():,}')

# Check for constant columns
const_cols = [col for col in df.columns if df[col].nunique() == 1]
if const_cols:
    print(f'Constant Columns (single unique value): {const_cols}')

# Data type summary
print(f'\nData Type Summary:')
print(df.dtypes.value_counts())

print('\n' + '=' * 80)
print('✓ STEP 1: EDA COMPLETE')
print('=' * 80)
print(f'\nOutputs saved to: {OUTPUT_DIR}/')
print('  - step1_clinical_distributions.png')
print('  - step1_correlation_matrix.png')
print('\nNext Steps:')
print('  1. Review the generated visualizations')
print('  2. Run Step 2 - Data Cleaning & Preprocessing')
print('  3. Run Step 3 - Model Training & Evaluation')
