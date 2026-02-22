import json
import os
from autovideo.utils.logger import logger
from autovideo.config.settings import settings

class ChannelService:
    def __init__(self):
        self.channels_file = os.path.join(os.getcwd(), 'autovideo_channels.json')
        self.channels = self._load_channels()
        self._ensure_default_channel()

    def _load_channels(self):
        if os.path.exists(self.channels_file):
            try:
                with open(self.channels_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error cargando canales: {e}")
        return {}

    def _save_channels(self):
        try:
            with open(self.channels_file, 'w') as f:
                json.dump(self.channels, f, indent=4)
        except Exception as e:
            logger.error(f"Error guardando canales: {e}")

    def _ensure_default_channel(self):
        """Asegura que el canal del .env esté siempre presente."""
        if settings.TARGET_CHANNEL_ID:
            chat_id = str(settings.TARGET_CHANNEL_ID)
            if chat_id not in self.channels:
                self.channels[chat_id] = {
                    'title': 'Canal Principal (.env)',
                    'type': 'channel'
                }
                self._save_channels()

    def add_channel(self, chat_id, title, chat_type):
        chat_id = str(chat_id)
        if chat_id not in self.channels:
            self.channels[chat_id] = {
                'title': title,
                'type': chat_type
            }
            self._save_channels()
            logger.info(f"Nuevo destino registrado: {title} ({chat_id})")

    def remove_channel(self, chat_id):
        chat_id = str(chat_id)
        if chat_id in self.channels:
            del self.channels[chat_id]
            self._save_channels()
            logger.info(f"Destino removido: {chat_id}")

    def get_all_destinations(self):
        return self.channels

channel_service = ChannelService()
