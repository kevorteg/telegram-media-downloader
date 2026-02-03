import os
from telegram import Update
from telegram.ext import ContextTypes
from autovideo.utils.url_utils import extract_urls
from autovideo.services.validator_service import is_supported_url
from autovideo.services.downloader_service import downloader_service
from autovideo.services.video_service import video_service
from autovideo.services.publish_service import publish_service
from autovideo.utils.file_utils import clean_directory
from autovideo.config.groups import get_destination_channels

from autovideo.services.history_service import history_service

async def handle_message_with_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    urls = extract_urls(text)
    if not urls:
        return

    # Solo procesamos la primera URL válida que encontremos para evitar spam
    target_url = None
    for url in urls:
        if is_supported_url(url):
            target_url = url
            break
    
    if not target_url:
        await update.message.reply_text("Enlace no soportado o inválido.")
        return

    # Verificar si ya se procesó
    if history_service.has_processed(target_url):
         await update.message.reply_text("⚠️ Este video ya fue enviado anteriormente.")
         return

    status_message = await update.message.reply_text("⏳ Descargando video...")

    try:
        # 1. Descargar (ahora retorna lista)
        media_list = downloader_service.download_video(target_url)
        
        if not media_list:
            await status_message.edit_text("❌ Error al descargar el video (posiblemente borrado o inaccesible).")
            return

        # 2. Procesar (Validar, comprimir si es necesario)
        processed_list = video_service.process_video(media_list)

        # 3. Publicar en canales destino
        await status_message.edit_text("📤 Enviando a los canales...")
        await publish_service.publish_video(context.bot, processed_list, caption=None)
        
        # 4. Modificación: NO enviar video al usuario (Chat Limpio)
        # Solo confirmación temporal
        await status_message.edit_text("✅ Enviado al canal.")

        # Marcar como procesado para no repetir
        history_service.mark_processed(target_url)

        # 5. Limpieza total
        # Borrar mensaje de confirmación del bot
        await status_message.delete()
        
        # Intentar borrar el mensaje original del usuario (el enlace)
        try:
            await update.message.delete()
        except:
            pass
        
        # 6. Limpieza de archivos
        for media in processed_list:
            if os.path.exists(media['path']):
                os.remove(media['path'])
        
        logger.info("Archivos temporales eliminados.")

    except Exception as e:
        await status_message.edit_text(f"❌ Ocurrió un error inesperado.")
        logger.error(f"Error procesando link: {e}")
        # Intentar limpiar en caso de error
        if 'media_list' in locals():
            for media in media_list:
                if os.path.exists(media['path']):
                    os.remove(media['path'])
