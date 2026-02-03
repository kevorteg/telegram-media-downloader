import sys
import os

# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from autovideo.config.settings import settings
from autovideo.utils.logger import logger
from autovideo.handlers.start_handler import start
from autovideo.handlers.link_handler import handle_message_with_links
from autovideo.handlers.admin_handler import admin_check
from autovideo.handlers.error_handler import error_handler

def main():
    logger.info("Iniciando AutoVideo Bot...")
    
    if not settings.TELEGRAM_TOKEN:
        logger.error("No se ha configurado el token del bot.")
        return

    application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

    # Agregar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_check))
    
    # Manejar mensajes de texto que no son comandos
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message_with_links))
    
    # Manejo de errores
    application.add_error_handler(error_handler)

    # Tareas Programadas (JobQueue)
    if settings.TWITTER_USERNAME:
        from autovideo.services.twitter_monitor_service import twitter_monitor
        job_queue = application.job_queue
        # Ejecutar cada 60 segundos (1 minuto) para pruebas más rápidas
        job_queue.run_repeating(twitter_monitor.check_new_likes, interval=60, first=10)
        logger.info(f"Monitor de Likes activado para @{settings.TWITTER_USERNAME}")
    else:
        logger.warning("Monitor de Likes NO activado (falta TWITTER_USERNAME en .env)")

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
