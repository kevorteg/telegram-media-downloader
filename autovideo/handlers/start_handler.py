from telegram import Update
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Hola {user.mention_html()}! Enviame un enlace de Twitter/X, Instagram o TikTok y trataré de descargar el video para ti.",
    )
