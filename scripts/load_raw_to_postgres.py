"""
Task 2 – Extract & Load (EL)
Load raw Telegram JSON data into PostgreSQL (raw schema)

This is a batch / one-off script.
Not part of application runtime.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

import psycopg2
from psycopg2.extras import execute_batch

# Project imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import DATA_PATHS, DATABASE_CONFIG
from src.logger import get_logger

logger = get_logger("load_raw_to_postgres")


# --------------------------------------------------
# Database utilities
# --------------------------------------------------

def get_db_connection():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        conn.autocommit = False
        logger.info("Connected to PostgreSQL successfully")
        return conn
    except Exception as e:
        logger.exception("Failed to connect to PostgreSQL")
        raise


def create_raw_table(conn):
    create_sql = """
    CREATE SCHEMA IF NOT EXISTS raw;

    CREATE TABLE IF NOT EXISTS raw.telegram_messages (
        message_id BIGINT,
        channel_name TEXT,
        message_date TIMESTAMP,
        message_text TEXT,
        has_media BOOLEAN,
        image_path TEXT,
        views INTEGER,
        forwards INTEGER,
        raw_payload JSONB
    );
    """

    with conn.cursor() as cur:
        cur.execute(create_sql)
        conn.commit()
        logger.info("raw.telegram_messages table is ready")


# --------------------------------------------------
# File handling
# --------------------------------------------------

def load_json_files(base_path: Path) -> List[Dict]:
    records = []

    if not base_path.exists():
        raise FileNotFoundError(f"Raw data path not found: {base_path}")

    for json_file in base_path.glob("*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for msg in data:
                records.append({
                    "message_id": msg.get("message_id"),
                    "channel_name": msg.get("channel_name"),
                    "message_date": msg.get("message_date"),
                    "message_text": msg.get("message_text"),
                    "has_media": msg.get("has_media", False),
                    "image_path": msg.get("image_path"),
                    "views": msg.get("views"),
                    "forwards": msg.get("forwards"),
                    "raw_payload": json.dumps(msg)
                })

            logger.info(f"Loaded {len(data)} records from {json_file.name}")

        except Exception as e:
            logger.exception(f"Failed reading {json_file.name}")

    return records


# --------------------------------------------------
# Load into Postgres
# --------------------------------------------------

def insert_records(conn, records: List[Dict]):
    if not records:
        logger.warning("No records found to insert")
        return

    insert_sql = """
    INSERT INTO raw.telegram_messages (
        message_id,
        channel_name,
        message_date,
        message_text,
        has_media,
        image_path,
        views,
        forwards,
        raw_payload
    ) VALUES (
        %(message_id)s,
        %(channel_name)s,
        %(message_date)s,
        %(message_text)s,
        %(has_media)s,
        %(image_path)s,
        %(views)s,
        %(forwards)s,
        %(raw_payload)s
    );
    """

    try:
        with conn.cursor() as cur:
            execute_batch(cur, insert_sql, records, page_size=500)
        conn.commit()
        logger.info(f"Inserted {len(records)} records into raw.telegram_messages")

    except Exception:
        conn.rollback()
        logger.exception("Failed inserting records")
        raise


# --------------------------------------------------
# Main entry point
# --------------------------------------------------

def main():
    print("Starting raw Telegram data load")

    try:
        raw_path = Path(DATA_PATHS["raw"]) / "telegram_messages" / "2026-01-17"

        conn = get_db_connection()
        create_raw_table(conn)

        records = load_json_files(raw_path)
        insert_records(conn, records)

        conn.close()
        print("✅ Task 2 Load completed successfully")

    except Exception as e:
        print("❌ Task 2 Load failed")
        print(e)


if __name__ == "__main__":
    main()
