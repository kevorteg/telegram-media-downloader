from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from autovideo.services.stats_service import stats_service
from autovideo.services.channel_service import channel_service
import asyncio

async def handle_message_with_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text: return

    all_urls = extract_urls(text)
    if not all_urls: return

    # Filtrar solo las URLs soportadas
    supported_urls = [u for u in all_urls if is_supported_url(u)]
    
    if not supported_urls:
        await update.message.reply_text("Enlace no soportado o inválido.")
        return

    # Limitar para evitar spam/saturación
    if len(supported_urls) > 10:
        await update.message.reply_text("⚠️ Demasiados enlaces en un mensaje. Solo procesaré los primeros 10.")
        supported_urls = supported_urls[:10]

    for target_url in supported_urls:
        if history_service.has_processed(target_url):
             await update.message.reply_text(f"⚠️ Este video ya fue enviado anteriormente:\n{target_url}")
             continue

        status_message = await update.message.reply_text(f"🔍 Analizando: {target_url}...")

        # Extraer formatos antes de descargar
        loop = asyncio.get_running_loop()
        try:
            formats = await loop.run_in_executor(None, lambda: downloader_service.get_available_formats(target_url))
        except Exception as e:
            logger.error(f"Error extrayendo info de {target_url}: {e}")
            await status_message.edit_text(f"❌ Error al obtener info de:\n{target_url}")
            continue
        
        if not formats:
            await status_message.edit_text(f"❌ No pude extraer la información de:\n{target_url}")
            continue

        # Guardar la URL en una referencia corta
        if 'pending_urls' not in context.user_data:
            context.user_data['pending_urls'] = {}
        
        if len(context.user_data['pending_urls']) > 30: # Aumento un poco el límite por si envían muchos
            first_key = next(iter(context.user_data['pending_urls']))
            del context.user_data['pending_urls'][first_key]
        
        url_ref = str(abs(hash(target_url)))[:10]
        context.user_data['pending_urls'][url_ref] = target_url

        # --- Lógica de procesamiento automático para Grupos Vinculados ---
        chat_id = str(update.effective_chat.id)
        destinations = channel_service.get_all_destinations()
        is_registered_group = chat_id in destinations

        if is_registered_group:
            logger.info(f"Procesamiento automático activado para el grupo: {chat_id}")
            await process_download(update, context, target_url, 'best', status_message)
            continue # Pasar al siguiente link
        # -----------------------------------------------------------------
        
        # Crear botones de resolución (Solo para chat privado)
        keyboard = []
        for f in formats:
            keyboard.append([InlineKeyboardButton(f"🎬 {f['height']}p ({f['ext']})", callback_data=f"q|{f['id']}|{url_ref}")])
        
        try:
            await status_message.edit_text(
                f"✨ <b>Video encontrado:</b>\n{target_url}\n\nSelecciona la calidad:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Error al enviar botones: {e}")
            await status_message.edit_text("❌ Error al generar las opciones de calidad.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data.split('|')
    action = data[0]

    if action == 'q':  # Calidad seleccionada
        format_id = data[1]
        url_ref = data[2]
        
        # Recuperar la URL original
        url = context.user_data.get('pending_urls', {}).get(url_ref)
        if not url:
            await query.message.edit_text("❌ Error: El enlace ha expirado o no se encuentra. Por favor, envía el link de nuevo.")
            return
            
        await process_download(update, context, url, format_id, query.message)
    
    elif action == 'dest': # Destino seleccionado
        chat_id = data[1]
        media_paths = context.user_data.get('pending_media', [])
        await finalize_sending(update, context, chat_id, media_paths)

async def process_download(update: Update, context: ContextTypes.DEFAULT_TYPE, url, format_id, status_message):
    # Generar referencia para los callbacks
    url_ref = str(abs(hash(url)))[:10]

    # 1. Descargar
    def update_progress(percent_str):
        try:
            p = int(float(percent_str.strip()))
            filled = p // 10
            bar = "█" * filled + "░" * (10 - filled)
            progress_text = f"⏳ Descargando... <code>[{bar}]</code> {p}%"
            if p % 10 == 0 or p >= 99:
                 asyncio.run_coroutine_threadsafe(
                    status_message.edit_text(progress_text, parse_mode='HTML'),
                    context.application.loop
                )
        except: pass

    await status_message.edit_text("⏳ Iniciando descarga...", reply_markup=None)
    
    loop = asyncio.get_running_loop()
    media_list = await loop.run_in_executor(
        None, lambda: downloader_service.download_video(url, progress_callback=update_progress, format_id=format_id)
    )
    
    if not media_list:
        await status_message.edit_text("❌ Error al descargar el video.")
        return

    # 2. Procesar (Solo arreglar metadatos, no comprimir auto)
    processed_list = video_service.process_video(media_list, auto_compress=False)
    if not processed_list: return
    
    media = processed_list[0]
    file_path = media['path']
    size_mb = media.get('size_mb', 0)
    
    # --- MENÚ DE VIDEO PESADO (> 50MB) ---
    if size_mb > 50:
        logger.warning(f"Video pesado detectado: {size_mb:.2f}MB")
        
        # Guardar info para los botones
        context.user_data['heavy_media'] = processed_list
        context.user_data['heavy_url'] = url
        
        keyboard = [
            [InlineKeyboardButton("📦 Comprimir (Sube a TG)", callback_data=f"heavy|compress|{url_ref}")],
            [InlineKeyboardButton("🔗 Ver Link Original", callback_data=f"heavy|link|{url_ref}")],
            [InlineKeyboardButton("⏭️ Saltar video", callback_data=f"heavy|skip|{url_ref}")]
        ]
        
        await status_message.edit_text(
            f"⚠️ <b>Video muy pesado!!</b> ({size_mb:.1f}MB)\n"
            f"Telegram solo permite subir hasta 50MB.\n\n"
            f"¿Qué quieres hacer?",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
        return
    # -------------------------------------

    # 3. Decidir destino (Menos de 50MB)
    chat_id = str(update.effective_chat.id)
    destinations = channel_service.get_all_destinations()
    
    # Si viene de un grupo vinculado, enviar allí directamente
    if chat_id in destinations:
        await finalize_sending(update, context, chat_id, processed_list, url, status_message)
        return

    # Si viene de privado o grupo no registrado, preguntar
    if len(destinations) > 1:
        keyboard = []
        for d_id, info in destinations.items():
            keyboard.append([InlineKeyboardButton(f"📡 {info['title']}", callback_data=f"dest|{d_id}")])
        
        if len(destinations) >= 2:
            keyboard.append([InlineKeyboardButton("📢 Ambos canales", callback_data="dest|all")])
        
        context.user_data['pending_media'] = processed_list
        context.user_data['pending_url'] = url
        
        await status_message.edit_text(
            "📍 <b>¿A dónde lo quieres enviar?</b>",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    else:
        # Solo uno (o ninguno registrado en JSON, usa env)
        target_id = next(iter(destinations.keys())) if destinations else settings.TARGET_CHANNEL_ID
        await finalize_sending(update, context, target_id, processed_list, url, status_message)

async def finalize_sending(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, media_list, url=None, status_message=None):
    if not status_message:
        status_message = update.callback_query.message if update.callback_query else None
    
    url = url or context.user_data.get('pending_url')
    
    if status_message:
        await status_message.edit_text("📤 Enviando contenido...")
    
    destinations = channel_service.get_all_destinations()
    targets = []

    if chat_id == 'all':
        targets = list(destinations.keys())
    else:
        targets = [chat_id]

    # 1. Enviar a destino(s) seleccionado(s)
    for target in targets:
        try:
            await publish_service.publish_video_to_chat(context.bot, media_list, target)
        except Exception as e:
            logger.error(f"Error enviando a {target}: {e}")
    
    # 2. Enviar al usuario (Persistencia) se mantiene como copia personal si es que el bot fue usado en privado
    if update.effective_chat.type == 'private':
        user_chat_id = update.effective_chat.id
        if str(user_chat_id) not in [str(t) for t in targets]:
            try:
                await publish_service.publish_video_to_chat(context.bot, media_list, user_chat_id)
            except: pass

    if status_message:
        await status_message.edit_text("✅ ¡Video entregado con éxito!")
        # Borrar el mensaje de éxito después de 5 segundos para mantener limpio el chat
        async def delete_success_msg():
            await asyncio.sleep(5)
            try: await status_message.delete()
            except: pass
        asyncio.create_task(delete_success_msg())
    
    if url:
        history_service.mark_processed(url)
        stats_service.log_download(update.effective_user.id)

    # Limpieza de archivos
    import os
    for media in media_list:
        if os.path.exists(media['path']):
            try: os.remove(media['path'])
            except: pass
    
    # Intentar borrar el link original (Solo si es un grupo o si es respuesta en privado)
    try: 
        msg_to_delete = update.message.message_id if not update.callback_query else update.callback_query.message.reply_to_message.message_id
        await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=msg_to_delete)
    except Exception as e: 
        logger.debug(f"No se pudo borrar el mensaje original: {e}")
