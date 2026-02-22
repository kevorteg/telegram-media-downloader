import telegram
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.config.groups import get_destination_channels

class PublishService:
    async def publish_video(self, bot: telegram.Bot, media_list: list[dict], caption: str = None):
        """Envía a TODOS los canales preconfigurados."""
        channels = get_destination_channels()
        for channel_id in channels:
            await self.publish_video_to_chat(bot, media_list, channel_id, caption)

    async def publish_video_to_chat(self, bot: telegram.Bot, media_list: list[dict], chat_id: str, caption: str = None):
        """Envía video(s) a un chat específico."""
        if not chat_id or not media_list:
            return

        # Caption: Firma personalizada
        caption = "👤 <b>KrimsonByte Hacked</b>"
        if update_user_link := "@KrimsonByte":
            caption = f"<a href='https://t.me/KrimsonByte'>{caption}</a>"

        try:
            logger.info(f"Enviando contenido a {chat_id}...")
            
            if len(media_list) == 1:
                media = media_list[0]
                with open(media['path'], 'rb') as video_file:
                    await bot.send_video(
                        chat_id=chat_id,
                        video=video_file,
                        caption=caption,
                        parse_mode='HTML',
                        width=media.get('width'),
                        height=media.get('height'),
                        duration=media.get('duration'),
                        supports_streaming=True
                    )
            else:
                input_media = []
                opened_files = []
                for i, media in enumerate(media_list):
                    f = open(media['path'], 'rb')
                    opened_files.append(f)
                    input_media.append(telegram.InputMediaVideo(
                        media=f,
                        caption=caption if i == 0 else None,
                        parse_mode='HTML' if i == 0 else None,
                        width=media.get('width'),
                        height=media.get('height'),
                        duration=media.get('duration'),
                        supports_streaming=True
                    ))
                
                if input_media:
                    await bot.send_media_group(chat_id=chat_id, media=input_media)
                
                for f in opened_files:
                    f.close()
            
            logger.info(f"Enviado con éxito a {chat_id}")
        except Exception as e:
            logger.error(f"Error al enviar a {chat_id}: {e}")

publish_service = PublishService()
