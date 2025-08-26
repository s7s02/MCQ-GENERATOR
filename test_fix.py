#!/usr/bin/env python3
"""
Test script to verify the import fix for mcqgenrator module
"""

import sys
import os

# Add the scr directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scr'))

try:
    # Test the fixed imports
    from mcqgenrator.MCQ import *
    from mcqgenrator.utils import read_file, get_table_data
    from mcqgenrator.logger import logging
    
    print("✅ SUCCESS: All imports working correctly!")
    print("✅ mcqgenrator module is now properly accessible")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("The fix may need additional adjustments")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
