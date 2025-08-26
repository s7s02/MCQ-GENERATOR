=======
import os
import sys
from dotenv import load_dotenv

# Handle both module and standalone execution
try:
    from .utils import read_file, get_table_data
except ImportError:
    # When running as standalone script
    from utils import read_file, get_table_data

# Load environment variables
load_dotenv()
