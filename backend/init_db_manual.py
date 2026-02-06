
import sys
import os
sys.path.append(os.path.abspath('.'))

import logging
logging.basicConfig(level=logging.INFO)

from models.database import init_db
from models.document import Document
from models.chunk import Chunk

try:
    print("Initializing Database Tables...")
    init_db()
    print("Database Tables Initialized Successfully!")
except Exception as e:
    print(f"Failed to initialize database: {e}")
    import traceback
    traceback.print_exc()
