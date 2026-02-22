from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = (
        f"<b>🚀 ¡Hola, {user.first_name}! Bienvenido a AutoVideo 2.0</b>\n\n"
        f"Soy tu asistente inteligente para descargar contenido de redes sociales.\n\n"
        f"✨ <b>¿Qué puedo hacer por ti?</b>\n"
        f"• Descargar videos de <b>Twitter (X), Instagram, TikTok</b>.\n"
        f"• Soporte universal para <b>YouTube Shorts</b> y más.\n"
        f"• Conversión automática y ahorro de datos.\n\n"
        f"📥 <i>Simplemente pega un enlace para comenzar...</i>"
    )
    await update.message.reply_text(message, parse_mode='HTML')
