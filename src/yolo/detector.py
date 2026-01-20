from ultralytics import YOLO
from pathlib import Path
from .classifier import classify_image
from .utils import extract_channel_and_message_id
import csv

model = YOLO("yolov8n.pt")

def run_yolo_pipeline(image_root: Path, output_csv: str):
    results_rows = []

    for image_path in image_root.rglob("*.jpg"):
        channel_code, message_id = extract_channel_and_message_id(image_path)

        detections = model(image_path, verbose=False)[0]

        detected_objects = [
            (model.names[int(box.cls)], float(box.conf))
            for box in detections.boxes
        ]

        if not detected_objects:
            continue

        image_category = classify_image(detected_objects)

        for label, confidence in detected_objects:
            results_rows.append({
                "message_id": message_id,
                "channel_code": channel_code,
                "detected_class": label,
                "confidence_score": round(confidence, 4),
                "image_category": image_category
            })

    _write_results(output_csv, results_rows)


def _write_results(output_csv: str, rows: list[dict]):
    if not rows:
        raise ValueError("No YOLO detections produced")

    fieldnames = rows[0].keys()

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
