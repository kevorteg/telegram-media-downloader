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
from autovideo.utils.logger import logger

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

    import asyncio
    
    try:
        # 1. Descargar (ahora retorna lista)
        # Función para actualizar progreso (se ejecuta en hilo de descarga)
        def update_progress(percent_str):
            try:
                # Filtrar actualizaciones para no floodear la API de Telegram
                # Solo actualizar cada 20% o cuando termine, o simularlo
                # Lo mejor es un "debounce" simple o solo actualizar cada X segundos.
                # Como es complicado pasar estado al callback simple, 
                # usaremos una aproximación: solo actualizar si cambia el primer dígito (cada 10%)
                # Ojo: esto corre en otro hilo, necesitamos schedulear la corrutina
                
                # Hack simple para rate limit: solo si termina en '0' o '5' (cada 5%)
                if percent_str.endswith('0') or percent_str.endswith('5'):
                     asyncio.run_coroutine_threadsafe(
                        status_message.edit_text(f"⏳ Descargando video... {percent_str}%"),
                        context.application.loop
                    )
            except Exception:
                pass

        # Ejecutar en executor para no bloquear el loop principal
        loop = asyncio.get_running_loop()
        media_list = await loop.run_in_executor(
            None, 
            lambda: downloader_service.download_video(target_url, progress_callback=update_progress)
        )
        
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
