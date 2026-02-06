
import sys
import os
sys.path.append(os.path.abspath('.'))

import logging
logging.basicConfig(level=logging.INFO)

from services.search_engine import get_search_service

try:
    print("Testing Search Service Initialization...")
    service = get_search_service()
    print("Search Service Initialized Successfully!")
except Exception as e:
    print(f"Failed to initialize Search Service: {e}")
    import traceback
    traceback.print_exc()
