import os
import sys

print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')[:10]}")

# Check if data file exists
data_file = 'outputs/clinical_data_raw.csv'
print(f"\nLooking for: {data_file}")
print(f"File exists: {os.path.exists(data_file)}")

if os.path.exists(data_file):
    print(f"File size: {os.path.getsize(data_file)} bytes")
    
    # Try to import and load
    try:
        import pandas as pd
        print("✓ pandas imported")
        
        print("Loading CSV...")
        df = pd.read_csv(data_file, nrows=10)
        print(f"✓ Loaded: {df.shape}")
        print(f"Columns: {list(df.columns)[:5]}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ File not found")
    print(f"Outputs folder contents: {os.listdir('outputs') if os.path.exists('outputs') else 'outputs/ not found'}")

print("\nDone!")
