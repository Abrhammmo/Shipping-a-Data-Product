from pathlib import Path
from src.config import DATA_PATHS
from src.logger import get_logger
import json

logger = get_logger("Storage")

def save_json(data, date_str, channel_name):
    try:
        # Use path from config
        path = DATA_PATHS["raw_messages"] / date_str
        path.mkdir(parents=True, exist_ok=True)

        file_path = path / f"{channel_name}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved JSON: {file_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save JSON for {channel_name}: {e}")
        return False


def save_image(image_bytes, channel_name, message_id):
    try:
        # Use path from config
        path = DATA_PATHS["raw_images"] / channel_name
        path.mkdir(parents=True, exist_ok=True)

        image_path = path / f"{message_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_bytes)

        logger.info(f"Saved image: {image_path}")
        return str(image_path)

    except Exception as e:
        logger.error(f"Failed to save image {message_id}: {e}")
        return None
