import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler, ChatMemberHandler
from telegram import Update, ChatMember
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.handlers.start_handler import start
from autovideo.handlers.link_handler import handle_message_with_links, handle_callback
from autovideo.handlers.admin_handler import admin_check
from autovideo.handlers.error_handler import error_handler
from autovideo.services.stats_service import stats_service
from autovideo.services.channel_service import channel_service

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_ids = settings.ADMIN_USER_IDS
    
    if user_id in admin_ids or not admin_ids:
        await update.message.reply_text(stats_service.get_stats_summary(), parse_mode='Markdown')
    else:
        await update.message.reply_text("🚫 No tienes permiso para ver estadísticas.")

async def on_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detecta cuando el bot es añadido a un canal o grupo."""
    result = update.my_chat_member
    if result.new_chat_member.status in [ChatMember.ADMINISTRATOR, ChatMember.MEMBER] :
        chat = result.chat
        channel_service.add_channel(chat.id, chat.title, chat.type)
    elif result.new_chat_member.status == ChatMember.LEFT:
        channel_service.remove_channel(result.chat.id)

def main():
    logger.info("Iniciando AutoVideo Bot...")
    
    if not settings.TELEGRAM_TOKEN:
        logger.error("No se ha configurado el token del bot.")
        return

    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    # Agregar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_check))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Manejar el estado del bot en chats (canales/grupos)
    application.add_handler(ChatMemberHandler(on_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    
    # Manejar selecciones interactivas (Calidad, Destino)
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # Manejar mensajes de texto que no son comandos
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message_with_links))
    
    # Manejo de errores
    application.add_error_handler(error_handler)

    logger.info("Bot en ejecución. Presiona Ctrl+C para detener.")
    application.run_polling()

def check_env_cookies():
    """
    Para despliegues en la nube (Koyeb/Render), permite pasar el contenido 
    de cookies.txt como una variable de entorno llamada COOKIES_CONTENT.
    """
    env_cookies = os.environ.get("COOKIES_CONTENT")
    if env_cookies:
        cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
        # Solo escribir si no existe o si queremos forzar actualización
        try:
            with open(cookies_path, 'w', encoding='utf-8') as f:
                f.write(env_cookies)
            logger.info("✅ Cookies cargadas desde variable de entorno COOKIES_CONTENT")
        except Exception as e:
            logger.error(f"❌ Error escribiendo cookies desde ENV: {e}")

if __name__ == '__main__':
    check_env_cookies()
    main()
