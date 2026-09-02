#!/usr/bin/env python
import sys
import os

# Write output to file since terminal capture isn't working
output_file = 'test_output.txt'

with open(output_file, 'w') as f:
    f.write("Test Script Starting\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Working directory: {os.getcwd()}\n")
    f.write(f"Files in directory: {os.listdir()}\n")
    
    # Test imports
    try:
        import pandas as pd
        f.write(f"✓ pandas {pd.__version__}\n")
    except ImportError as e:
        f.write(f"✗ pandas import failed: {e}\n")
    
    try:
        import numpy as np
        f.write(f"✓ numpy {np.__version__}\n")
    except ImportError as e:
        f.write(f"✗ numpy import failed: {e}\n")
    
    try:
        import matplotlib
        f.write(f"✓ matplotlib {matplotlib.__version__}\n")
    except ImportError as e:
        f.write(f"✗ matplotlib import failed: {e}\n")

    f.write("\nTest complete\n")

print(f"Output written to {output_file}")

# Also print so we can see it
with open(output_file, 'r') as f:
    print(f.read())
