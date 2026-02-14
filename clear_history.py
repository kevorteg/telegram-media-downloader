
import sqlite3
import os
from autovideo.services.history_service import DB_PATH

if os.path.exists(DB_PATH):
    try:
        os.remove(DB_PATH)
        print("History database deleted successfully.")
    except Exception as e:
        print(f"Error deleting database: {e}")
else:
    print("Database not found.")
