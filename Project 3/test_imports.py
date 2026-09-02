#!/usr/bin/env python
import os
import sys

# Write to temp directory where permissions are guaranteed
temp_dir = os.path.expandvars(r'%TEMP%')
status_file = os.path.join(temp_dir, 'eda_status.txt')

with open(status_file, 'w') as f:
    f.write("EDA Status Report\n")
    f.write(f"Current directory: {os.getcwd()}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Temp directory: {temp_dir}\n")
    
    # Check if data file exists
    data_path = r'C:\Users\swarn\Bootcamp-P3\outputs\clinical_data_raw.csv'
    f.write(f"\nData file exists: {os.path.exists(data_path)}\n")
    
    if os.path.exists(data_path):
        f.write(f"Data file size: {os.path.getsize(data_path):,} bytes\n")
    
    f.write("\nAttempting to import libraries...\n")
    
    try:
        import pandas as pd
        f.write(f"✓ pandas {pd.__version__}\n")
    except ImportError as e:
        f.write(f"✗ pandas: {e}\n")
    
    try:
        import numpy as np
        f.write(f"✓ numpy {np.__version__}\n")
    except ImportError as e:
        f.write(f"✗ numpy: {e}\n")
    
    try:
        import matplotlib
        f.write(f"✓ matplotlib {matplotlib.__version__}\n")
    except ImportError as e:
        f.write(f"✗ matplotlib: {e}\n")
    
    try:
        import seaborn
        f.write(f"✓ seaborn {seaborn.__version__}\n")
    except ImportError as e:
        f.write(f"✗ seaborn: {e}\n")

print(f"Status written to: {status_file}")

# Try to read and display it
try:
    with open(status_file, 'r') as f:
        print(f.read())
except:
    print("Could not read status file")
