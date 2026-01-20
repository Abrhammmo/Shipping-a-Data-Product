import sys
import os
# Add parent directory to path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from src.config import DATABASE_CONFIG

def load_yolo_csv_to_postgres(csv_path: str):
    engine = create_engine(
        f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
        f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}"
    )

    df = pd.read_csv(csv_path)

    # Select only columns for raw table
    df = df[['message_id', 'detected_class', 'confidence_score', 'image_category']]

    df.to_sql(
        "yolo_detections",
        engine,
        schema="raw",
        if_exists="append",
        index=False
    )

    print("✅ YOLO detections loaded into PostgreSQL")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "yolo_detections.csv")
    load_yolo_csv_to_postgres(csv_path)
