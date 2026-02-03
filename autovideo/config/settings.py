import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
    ADMIN_USER_IDS = [int(id.strip()) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id.strip()]
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "autovideo/storage/temp")
    
    # Credenciales opcionales para Twitter/X
    TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
    
    # Validaciones básicas
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN no está definido en .env")

settings = Settings()
