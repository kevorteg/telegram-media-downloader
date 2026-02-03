import logging
from telegram import Update
from telegram.ext import ContextTypes
from autovideo.utils.logger import logger

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
