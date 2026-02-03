from autovideo.config.settings import settings

# En el futuro esto podría leer de una base de datos o archivo JSON.
# Por ahora, usamos una lista simple con el canal principal del .env

DESTINATION_CHANNELS = []

if settings.TARGET_CHANNEL_ID:
    DESTINATION_CHANNELS.append(settings.TARGET_CHANNEL_ID)

def get_destination_channels():
    return DESTINATION_CHANNELS
