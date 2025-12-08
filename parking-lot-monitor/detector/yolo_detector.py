# detector/yolo_detector.py

from ultralytics import YOLO
from config import YOLO_MODEL_PATH, VEHICLE_CLASSES

class YOLODetector:
    def __init__(self):
        self.model = YOLO(YOLO_MODEL_PATH)

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]

        # ⭐ DEBUG PRINT — shows ALL detected class IDs every frame
        print("RAW YOLO DETECTIONS:", results.boxes.cls.tolist())

        detections = []
        for box in results.boxes:
            cls = int(box.cls)

            # Filter out non-vehicle classes
            if cls not in VEHICLE_CLASSES:
                continue

            x1, y1, x2, y2 = box.xyxy[0]
            conf = float(box.conf)

            detections.append({
                "box": (int(x1), int(y1), int(x2), int(y2)),
                "class": cls,
                "confidence": conf,
            })

        return detections
