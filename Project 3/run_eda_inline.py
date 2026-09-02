"""
Inline EDA Execution with Status Tracking
"""
import os
import sys

# Ensure we're in the right directory
os.chdir(r'C:\Users\swarn\Bootcamp-P3')

status_file = 'step1_execution_status.txt'

with open(status_file, 'w') as f:
    try:
        f.write("Step 1 EDA Execution Starting...\n")
        f.flush()
        
        # Import all required libraries
        import pandas as pd
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        import warnings
        warnings.filterwarnings('ignore')
        
        f.write("✓ Imports successful\n")
        f.flush()
        
        # Configuration
        DATA_PATH = 'outputs/clinical_data_raw.csv'
        OUTPUT_DIR = 'outputs'
        TARGET = 'Readmission_30d'
        
        # Load data
        f.write(f"Loading {DATA_PATH}...\n")
        f.flush()
        df = pd.read_csv(DATA_PATH)
        
        f.write(f"✓ Loaded {df.shape[0]:,} rows x {df.shape[1]} columns\n")
        f.flush()
        
        # Generate distribution plots
        f.write("Creating distribution plots...\n")
        f.flush()
        
        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        numeric_cols = [c for c in numeric_cols if c not in ['patient_id', 'Patient_ID', 'unnamed_0', 'Unnamed: 0']]
        
        fig, axes = plt.subplots(3, 3, figsize=(15, 12))
        axes = axes.flatten()
        
        for i, (ax, col) in enumerate(zip(axes, numeric_cols[:9])):
            try:
                sns.histplot(df[col], kde=True, ax=ax, color='teal', bins=30)
                ax.set_title(f'Distribution of {col}')
            except Exception as e:
                ax.text(0.5, 0.5, f'Error: {str(e)[:50]}', ha='center', va='center')
        
        for i in range(len(numeric_cols), 9):
            axes[i].axis('off')
        
        plt.tight_layout()
        output_file = f'{OUTPUT_DIR}/step1_clinical_distributions.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close()
        
        f.write(f"✓ Saved {output_file}\n")
        f.flush()
        
        # Generate correlation heatmap
        f.write("Creating correlation heatmap...\n")
        f.flush()
        
        plt.figure(figsize=(14, 10))
        corr = df[numeric_cols].corr()
        sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt='.2f', 
                   square=True, linewidths=0.5)
        plt.title('Feature Correlation Matrix')
        plt.tight_layout()
        output_file2 = f'{OUTPUT_DIR}/step1_correlation_matrix.png'
        plt.savefig(output_file2, dpi=150, bbox_inches='tight')
        plt.close()
        
        f.write(f"✓ Saved {output_file2}\n")
        f.flush()
        
        # Verify files exist
        f.write("\nVerifying output files...\n")
        f.flush()
        
        if os.path.exists('outputs/step1_clinical_distributions.png'):
            size1 = os.path.getsize('outputs/step1_clinical_distributions.png')
            f.write(f"✓ step1_clinical_distributions.png exists ({size1:,} bytes)\n")
        else:
            f.write("✗ step1_clinical_distributions.png NOT FOUND\n")
        f.flush()
        
        if os.path.exists('outputs/step1_correlation_matrix.png'):
            size2 = os.path.getsize('outputs/step1_correlation_matrix.png')
            f.write(f"✓ step1_correlation_matrix.png exists ({size2:,} bytes)\n")
        else:
            f.write("✗ step1_correlation_matrix.png NOT FOUND\n")
        f.flush()
        
        f.write("\n✓✓✓ STEP 1 EDA COMPLETED SUCCESSFULLY ✓✓✓\n")
        f.flush()
        
    except Exception as e:
        import traceback
        f.write(f"\n✗ ERROR: {str(e)}\n")
        f.write(traceback.format_exc())
        f.flush()

# Try to print the status file to console
try:
    with open(status_file, 'r') as f:
        print(f.read())
except:
    pass

sys.exit(0)
