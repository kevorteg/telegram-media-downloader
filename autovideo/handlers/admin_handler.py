from telegram import Update
from telegram.ext import ContextTypes
from autovideo.config.permissions import is_admin

async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_admin(user.id):
        await update.message.reply_text("Eres administrador.")
    else:
        await update.message.reply_text("No eres administrador.")
