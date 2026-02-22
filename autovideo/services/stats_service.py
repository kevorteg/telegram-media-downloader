import json
import os
from datetime import datetime
from autovideo.utils.logger import logger

class StatsService:
    def __init__(self):
        self.stats_file = os.path.join(os.getcwd(), 'autovideo_stats.json')
        self.stats = self._load_stats()

    def _load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando estadísticas: {e}")
        
        return {
            'total_downloads': 0,
            'total_users': [],
            'start_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _save_stats(self):
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando estadísticas: {e}")

    def log_download(self, user_id):
        self.stats['total_downloads'] += 1
        if user_id not in self.stats['total_users']:
            self.stats['total_users'].append(user_id)
        self._save_stats()

    def get_stats_summary(self):
        return (
            f"📊 *Estadísticas del Bot*\n\n"
            f"📥 Total descargas: `{self.stats['total_downloads']}`\n"
            f"👤 Usuarios únicos: `{len(self.stats['total_users'])}`\n"
            f"📅 Activo desde: `{self.stats['start_date']}`"
        )

stats_service = StatsService()
