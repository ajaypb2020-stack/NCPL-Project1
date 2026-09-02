#!/usr/bin/env python
"""
Quick test script to verify environment and data loading
"""
import sys
import os
print(f"Python: {sys.version}")
print(f"CWD: {os.getcwd()}")

# Test imports
try:
    import pandas as pd
    print("✓ pandas imported")
except Exception as e:
    print(f"✗ pandas error: {e}")
    sys.exit(1)

try:
    import matplotlib
    print("✓ matplotlib imported")
except Exception as e:
    print(f"✗ matplotlib error: {e}")

# Test data file
data_path = 'outputs/clinical_data_raw.csv'
print(f"\nChecking data file: {data_path}")
if os.path.exists(data_path):
    print(f"✓ File exists: {os.path.getsize(data_path)} bytes")
    try:
        df = pd.read_csv(data_path, nrows=5)
        print(f"✓ Loaded successfully: {df.shape} (first 5 rows)")
        print(f"Columns: {list(df.columns)[:5]}...")
    except Exception as e:
        print(f"✗ Load error: {e}")
else:
    print(f"✗ File not found")
    print(f"Files in outputs/: {os.listdir('outputs') if os.path.exists('outputs') else 'outputs/ not found'}")

print("\n✓ Test complete")
