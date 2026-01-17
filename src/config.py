"""
Central configuration file for the Medical Telegram Data Warehouse
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# -------------------------------------------------------------------
# Load environment variables
# -------------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------------
# Telegram API Configuration
# -------------------------------------------------------------------
TELEGRAM_CONFIG = {
    "api_id": int(os.getenv("TELEGRAM_API_ID")),
    "api_hash": os.getenv("TELEGRAM_API_HASH"),
    "session_name": os.getenv("TELEGRAM_SESSION_NAME", "medical_scraper"),
}

# -------------------------------------------------------------------
# Telegram Channels Configuration
# key   -> internal channel code (used in warehouse)
# value -> Telegram username (without https://t.me/)
# -------------------------------------------------------------------
TELEGRAM_CHANNELS = {
    # "CHEMED": "CheMed123",
    # "LOBELIA": "lobelia4cosmetics",
    "TIKVAH": "tikvahpharma"
    # "RAYA": "rayapharmaceuticals",
    # "CAFIMAD": "CafimadD",
    # "NEW_OPTICS": "newoptics",
    # "VIMAX": "Vimax123",
}

# -------------------------------------------------------------------
# Channel Metadata (used later in dim_channels)
# -------------------------------------------------------------------
CHANNEL_METADATA = {
    # "CHEMED": {"channel_type": "Medical"},
    # "LOBELIA": {"channel_type": "Cosmetics"},
    "TIKVAH": {"channel_type": "Pharmaceutical"}
    # "RAYA": {"channel_type": "Pharmaceutical"},
    # "CAFIMAD": {"channel_type": "Pharmaceutical"},
    # "NEW_OPTICS": {"channel_type": "Medical"},
    # "VIMAX": {"channel_type": "Medical"},
}

# -------------------------------------------------------------------
# Scraping Configuration
# -------------------------------------------------------------------
SCRAPING_CONFIG = {
    "max_messages_per_channel": int(os.getenv("MAX_MESSAGES", 0)),  # 0 = no limit
    "max_retries": int(os.getenv("MAX_RETRIES", 3)),
    "sleep_seconds": int(os.getenv("SCRAPER_SLEEP", 2)),
}

# -------------------------------------------------------------------
# Data Lake Paths
# -------------------------------------------------------------------
BASE_DATA_DIR = Path(__file__).parent.parent / "data"

DATA_PATHS = {
    "raw": BASE_DATA_DIR / "raw",
    "raw_messages": BASE_DATA_DIR / "raw" / "telegram_messages",
    "raw_images": BASE_DATA_DIR / "raw" / "images",
}

# -------------------------------------------------------------------
# Logging Configuration
# -------------------------------------------------------------------
LOGGING_CONFIG = {
    "log_dir": Path("../data/logs"),
    "log_file": "scraper.log",
}
