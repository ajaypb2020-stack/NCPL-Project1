#!/usr/bin/env python
"""Step 1 EDA - Complete with verification"""
import os
import sys
os.chdir(r'C:\Users\swarn\Bootcamp-P3')

# Set unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("STEP 1: EXPLORATORY DATA ANALYSIS (EDA)")
print("="*80)

# Configuration
DATA_PATH = 'outputs/clinical_data_raw.csv'
OUTPUT_DIR = 'outputs'
TARGET = 'Readmission_30d'

print(f'\nLoading data from: {DATA_PATH}')

# Load data
df = pd.read_csv(DATA_PATH)
print(f'✓ Loaded {df.shape[0]:,} rows x {df.shape[1]} columns')

# Basic info
print(f'\nDataset Shape: {df.shape}')
print(f'\nFirst 5 rows:')
print(df.head())

print(f'\nColumn Types:')
print(df.dtypes)

print(f'\nDescriptive Statistics:')
print(df.describe())

# Missing values
print(f'\nMissing Values:')
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
    print("No missing values")

# Target distribution
print(f'\nTarget Variable Distribution ({TARGET}):')
if TARGET in df.columns:
    print(df[TARGET].value_counts().sort_index())
    print('\nPercentages:')
    print((df[TARGET].value_counts(normalize=True).sort_index() * 100).round(2))
else:
    print(f'Target "{TARGET}" not found')
    print(f'Available: {list(df.columns)}')

# Distribution plots
print(f'\nCreating distribution plots...')
numeric_cols = df.select_dtypes(include='number').columns.tolist()
numeric_cols = [c for c in numeric_cols if c not in ['patient_id', 'Patient_ID', 'unnamed_0', 'Unnamed: 0']]

fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.flatten()

for i, (ax, col) in enumerate(zip(axes, numeric_cols[:9])):
    sns.histplot(df[col], kde=True, ax=ax, color='teal', bins=30)
    ax.set_title(f'Distribution of {col}')

for i in range(len(numeric_cols), 9):
    axes[i].axis('off')

plt.tight_layout()
dist_file = f'{OUTPUT_DIR}/step1_clinical_distributions.png'
plt.savefig(dist_file, dpi=150, bbox_inches='tight')
plt.close()
print(f'✓ Saved: {dist_file}')

# Correlation heatmap
print(f'Creating correlation heatmap...')
plt.figure(figsize=(14, 10))
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt='.2f', 
           square=True, linewidths=0.5, cbar_kws={'label': 'Correlation'})
plt.title('Feature Correlation Matrix')
plt.tight_layout()
corr_file = f'{OUTPUT_DIR}/step1_correlation_matrix.png'
plt.savefig(corr_file, dpi=150, bbox_inches='tight')
plt.close()
print(f'✓ Saved: {corr_file}')

# Data quality summary
print(f'\nData Quality Summary:')
print(f'Duplicate rows: {df.duplicated().sum():,}')
const_cols = [col for col in df.columns if df[col].nunique() == 1]
if const_cols:
    print(f'Constant columns: {const_cols}')
print(f'Data types: {df.dtypes.value_counts().to_dict()}')

print("\n" + "="*80)
print("✓✓✓ STEP 1 EDA COMPLETED ✓✓✓")
print("="*80)
print(f'\nOutputs saved to: {OUTPUT_DIR}/')
print('  - step1_clinical_distributions.png')
print('  - step1_correlation_matrix.png')
print('\nNext: Run Step 2 - Data Cleaning & Preprocessing')
