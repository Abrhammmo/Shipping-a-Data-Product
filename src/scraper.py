import asyncio
from datetime import datetime
from tqdm import tqdm
from telethon.tl.types import MessageMediaPhoto

from src.config import TELEGRAM_CHANNELS, SCRAPING_CONFIG
from src.telegram_client import create_client
from src.storage import save_json, save_image
from src.logger import get_logger

logger = get_logger("Scraper")


async def scrape_channel(client, channel_code, channel_username):
    """
    Scrape messages from a single Telegram channel
    """
    records = []
    limit = SCRAPING_CONFIG["max_messages_per_channel"] or None

    async for message in client.iter_messages(channel_username, limit=limit):
        try:
            record = {
                "message_id": message.id,
                "channel_code": channel_code,
                "channel_name": channel_username,
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.text,
                "views": message.views,
                "forwards": message.forwards,
                "has_media": bool(message.media),
                "image_path": None,
            }

            # If message has an image, save it
            if isinstance(message.media, MessageMediaPhoto):
                image_bytes = await client.download_media(message.media, file=bytes)
                record["image_path"] = save_image(
                    image_bytes, channel_username, message.id
                )

            records.append(record)

        except Exception as e:
            logger.error(
                f"Failed message | channel={channel_username} | id={message.id} | {e}"
            )

    logger.info(f"Scraped {len(records)} messages from {channel_username}")
    return records


async def run_scraper():
    """
    Main scraper function
    """
    client = create_client()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    try:
        await client.start()
        logger.info("Telegram scraper started")

        for code, username in tqdm(TELEGRAM_CHANNELS.items(), desc="Channels"):
            try:
                logger.info(f"Starting scrape for channel: {username}")
                data = await scrape_channel(client, code, username)
                success = save_json(data, today, username)

                if success:
                    logger.info(f"Channel SUCCESS: {username}")
                else:
                    logger.warning(f"Channel PARTIAL FAILURE: {username}")

            except Exception as e:
                logger.error(f"Channel scrape FAILED: {username} | {e}")

        logger.info("All channels scraped successfully")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.critical(f"Scraping pipeline FAILED completely: {e}")
        return {"status": "FAILED"}

    finally:
        await client.disconnect()
