from telethon import TelegramClient
from src.config import TELEGRAM_CONFIG
from src.logger import get_logger

logger = get_logger("TelegramClient")

def create_client():
    try:
        client = TelegramClient(
            TELEGRAM_CONFIG["session_name"],
            TELEGRAM_CONFIG["api_id"],
            TELEGRAM_CONFIG["api_hash"],
        )
        logger.info("Telegram client initialized")
        return client

    except Exception as e:
        logger.critical(f"Telegram client creation failed: {e}")
        raise
