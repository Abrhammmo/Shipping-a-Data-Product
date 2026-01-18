import json
from pathlib import Path
from datetime import datetime

RAW_DATA_PATH = Path("data/raw/telegram_messages")

REQUIRED_FIELDS = {
    "message_id",
    "channel_name",
    "message_date",
    "message_text",
    "views",
    "forwards",
    "has_media"
}


def test_raw_telegram_json_integrity():
    assert RAW_DATA_PATH.exists(), "Raw data directory does not exist"

    json_files = list(RAW_DATA_PATH.rglob("*.json"))
    assert json_files, "No raw Telegram JSON files found"

    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            records = json.load(f)

        assert isinstance(records, list), f"{file} does not contain a list"

        message_ids = set()

        for record in records:
            # Required fields check
            missing = REQUIRED_FIELDS - record.keys()
            assert not missing, f"{file} missing fields: {missing}"

            # message_id uniqueness
            msg_id = record["message_id"]
            assert msg_id not in message_ids, f"Duplicate message_id {msg_id} in {file}"
            message_ids.add(msg_id)

            # message_date validity
            try:
                datetime.fromisoformat(record["message_date"])
            except Exception:
                raise AssertionError(f"Invalid message_date in {file}: {record['message_date']}")

            # Non-negative numeric checks
            assert record["views"] >= 0, f"Negative views in {file}"
            assert record["forwards"] >= 0, f"Negative forwards in {file}"

            # Media consistency
            if record["has_media"]:
                assert record.get("image_path"), f"Missing image_path for media message in {file}"
