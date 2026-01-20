import sys
from yolo.detector import run_yolo_pipeline

if __name__ == "__main__":
    try:
        run_yolo_pipeline()
        print(" YOLO detections generated.")
    except Exception as e:
        print(f"❌ Task 3 failed: {e}")
        sys.exit(1)
