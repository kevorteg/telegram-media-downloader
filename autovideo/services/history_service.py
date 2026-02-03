import sqlite3
import os
from autovideo.utils.logger import logger

DB_PATH = "autovideo/storage/history.db"

class HistoryService:
    def __init__(self):
        self.ensure_db()

    def ensure_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS downloads
                     (url TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def has_processed(self, url: str) -> bool:
        """Verifica si una URL ya fue procesada."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 1 FROM downloads WHERE url = ?", (url,))
        result = c.fetchone()
        conn.close()
        return result is not None

    def mark_processed(self, url: str):
        """Marca una URL como procesada."""
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO downloads (url) VALUES (?)", (url,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error al guardar historial para {url}: {e}")

history_service = HistoryService()
