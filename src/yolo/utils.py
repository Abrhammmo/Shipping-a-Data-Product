from pathlib import Path

def extract_channel_and_message_id(image_path: Path) -> tuple[str, str]:
    """
    Extract channel_code and message_id from image path.

    Expected structure:
    data/raw/images/{channel_code}/{message_id}.jpg
    """
    channel_code = image_path.parent.name
    message_id = image_path.stem
    return channel_code, message_id
