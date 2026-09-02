#!/usr/bin/env python
"""
Step 1 EDA - Writes results to file
"""
import os
import sys

# Force immediate unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

output_file = 'C:\\Users\\swarn\\Bootcamp-P3\\step1_results.txt'

try:
    with open(output_file, 'w', buffering=1) as log:
        log.write("="*80 + "\n")
        log.write("STEP 1: EXPLORATORY DATA ANALYSIS (EDA)\n")
        log.write("="*80 + "\n")
        log.flush()
        
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import warnings
        warnings.filterwarnings('ignore')
        
        log.write("\n✓ All imports successful\n")
        log.flush()
        
        DATA_PATH = 'outputs/clinical_data_raw.csv'
        OUTPUT_DIR = 'outputs'
        TARGET = 'Readmission_30d'
        
        log.write(f'\nLoading data from: {DATA_PATH}\n')
        log.flush()
        
        if not os.path.exists(DATA_PATH):
            log.write(f'ERROR: File not found: {DATA_PATH}\n')
            log.flush()
            sys.exit(1)
        
        df = pd.read_csv(DATA_PATH)
        log.write(f'✓ Successfully loaded\n')
        log.flush()
        
        log.write(f'\nDataset Shape: {df.shape}\n')
        log.write(f'  Rows: {df.shape[0]:,} patients\n')
        log.write(f'  Columns: {df.shape[1]} features\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('COLUMN TYPES\n')
        log.write('='*80 + '\n')
        log.write(str(df.dtypes) + '\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('FIRST 5 ROWS\n')
        log.write('='*80 + '\n')
        log.write(df.head().to_string() + '\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('DESCRIPTIVE STATISTICS\n')
        log.write('='*80 + '\n')
        log.write(df.describe().to_string() + '\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('MISSING VALUES\n')
        log.write('='*80 + '\n')
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            null_df = pd.DataFrame({
                'Column': null_counts.index,
                'Null_Count': null_counts.values,
                'Null_%': (null_counts.values / len(df) * 100).round(2)
            })
            null_df = null_df[null_df['Null_Count'] > 0].sort_values('Null_Count', ascending=False)
            log.write(null_df.to_string(index=False) + '\n')
        else:
            log.write("No missing values found.\n")
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('TARGET VARIABLE DISTRIBUTION\n')
        log.write('='*80 + '\n')
        if TARGET in df.columns:
            log.write(f'\nTarget: {TARGET}\n')
            log.write('\nValue Counts:\n')
            log.write(str(df[TARGET].value_counts().sort_index()) + '\n')
            log.write('\nPercentage Distribution:\n')
            log.write(str((df[TARGET].value_counts(normalize=True).sort_index().round(4) * 100)) + '\n')
        else:
            log.write(f'WARNING: Target column "{TARGET}" not found in dataset\n')
            log.write(f'Available columns: {list(df.columns)}\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('GENERATING DISTRIBUTION PLOTS\n')
        log.write('='*80 + '\n')
        
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['patient_id', 'Patient_ID', 'unnamed_0', 'Unnamed: 0']]
        
        if len(numeric_cols) > 0:
            log.write(f'Creating histograms for {len(numeric_cols)} numeric columns...\n')
            fig, axes = plt.subplots(3, 3, figsize=(15, 12))
            axes = axes.flatten()
            
            for i, (ax, col) in enumerate(zip(axes, numeric_cols[:9])):
                try:
                    sns.histplot(df[col], kde=True, ax=ax, color='teal', bins=30)
                    ax.set_title(f'Distribution of {col}')
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error plotting {col}', ha='center', va='center')
            
            for i in range(len(numeric_cols), 9):
                axes[i].axis('off')
            
            plt.tight_layout()
            output_file_png = f'{OUTPUT_DIR}/step1_clinical_distributions.png'
            plt.savefig(output_file_png, dpi=150, bbox_inches='tight')
            plt.close()
            log.write(f'✓ Saved distribution plots to: {output_file_png}\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('GENERATING CORRELATION HEATMAP\n')
        log.write('='*80 + '\n')
        
        if len(numeric_cols) > 1:
            log.write(f'Computing correlation for {len(numeric_cols)} numeric columns...\n')
            plt.figure(figsize=(14, 10))
            corr = df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt='.2f', 
                       square=True, linewidths=0.5, cbar_kws={'label': 'Correlation'})
            plt.title('Feature Correlation Matrix')
            plt.tight_layout()
            output_file_png2 = f'{OUTPUT_DIR}/step1_correlation_matrix.png'
            plt.savefig(output_file_png2, dpi=150, bbox_inches='tight')
            plt.close()
            log.write(f'✓ Saved correlation heatmap to: {output_file_png2}\n')
        log.flush()
        
        log.write('\n' + '='*80 + '\n')
        log.write('DATA QUALITY SUMMARY\n')
        log.write('='*80 + '\n')
        log.write(f'\nDuplicate Rows: {df.duplicated().sum():,}\n')
        
        const_cols = [col for col in df.columns if df[col].nunique() == 1]
        if const_cols:
            log.write(f'Constant Columns: {const_cols}\n')
        
        log.write(f'\nData Type Summary:\n')
        log.write(str(df.dtypes.value_counts()) + '\n')
        
        log.write('\n' + '='*80 + '\n')
        log.write('✓ STEP 1: EDA COMPLETE\n')
        log.write('='*80 + '\n')
        log.flush()

except Exception as e:
    with open(output_file, 'a') as log:
        log.write(f'\n\nERROR: {str(e)}\n')
        import traceback
        log.write(traceback.format_exc())
    raise
