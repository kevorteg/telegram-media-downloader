import telegram
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.config.groups import get_destination_channels

class PublishService:
    async def publish_video(self, bot: telegram.Bot, media_list: list[dict], caption: str = None):
        """
        Envía video(s) a los canales configurados.
        Soporta envío individual o como álbum (MediaGroup).
        """
        channels = get_destination_channels()
        if not channels or not media_list:
            return

        for channel_id in channels:
            try:
                logger.info(f"Enviando {len(media_list)} archivos a {channel_id}...")
                
                # Si es solo uno, usamos send_video normal (mejor control de dimensiones)
                if len(media_list) == 1:
                    media = media_list[0]
                    with open(media['path'], 'rb') as video_file:
                        await bot.send_video(
                            chat_id=channel_id,
                            video=video_file,
                            caption=caption,
                            width=media.get('width'),
                            height=media.get('height'),
                            duration=media.get('duration'),
                            supports_streaming=True
                        )
                
                # Si son varios, usamos send_media_group (Álbum)
                else:
                    # Telegram requiere InputMediaVideo para álbumes
                    input_media = []
                    opened_files = [] # Para cerrarlos después
                    
                    for i, media in enumerate(media_list):
                        f = open(media['path'], 'rb')
                        opened_files.append(f)
                        
                        input_media.append(telegram.InputMediaVideo(
                            media=f,
                            caption=caption if i == 0 else None, # Caption solo en el primero
                            width=media.get('width'),
                            height=media.get('height'),
                            duration=media.get('duration'),
                            supports_streaming=True
                        ))
                    
                    if input_media:
                        await bot.send_media_group(chat_id=channel_id, media=input_media)
                    
                    # Cerrar archivos
                    for f in opened_files:
                        f.close()
                        
                logger.info(f"Contenido enviado correctamente a {channel_id}")
            except Exception as e:
                logger.error(f"Error al enviar a {channel_id}: {e}")

publish_service = PublishService()
