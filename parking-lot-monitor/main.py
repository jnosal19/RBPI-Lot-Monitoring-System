# main.py

import os
import time
import cv2

from camera import Camera
from detector.yolo_detector import YOLODetector
from detector.roi_utils import box_intersects_roi
from detector.state_machine import PresenceStateMachine
from notifier.webhook_notifier import WebhookNotifier

from config import (
    ROI,
    SNAPSHOT_DIR,
    YOLO_EVERY_N_FRAMES,
)

def save_snapshot(frame):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    filename = time.strftime("snapshot_%Y%m%d_%H%M%S.jpg")
    path = os.path.join(SNAPSHOT_DIR, filename)
    cv2.imwrite(path, frame)
    return path

def main():
    cam = Camera()
    cam.open()

    detector = YOLODetector()
    state_machine = PresenceStateMachine()
    notifier = WebhookNotifier()

    frame_count = 0

    print("Parking lot monitor running... Press Ctrl+C to stop.")

    while True:
        frame = cam.read()
        frame_count += 1

        # YOLO every N frames
        should_run_yolo = (frame_count % YOLO_EVERY_N_FRAMES == 0)

        vehicle_present = False

        if should_run_yolo:
            detections = detector.detect(frame)

            for det in detections:
                if box_intersects_roi(det["box"], ROI):
                    vehicle_present = True
                    break

        # Update state machine
        event = state_machine.update(vehicle_present)

        # Trigger notifications
        if event == "ENTER":
            snapshot = save_snapshot(frame)
            notifier.send("Vehicle ENTERED lot", f"Time: {time.ctime()}", snapshot)

        elif event == "EXIT":
            snapshot = save_snapshot(frame)
            notifier.send("Vehicle EXITED lot", f"Time: {time.ctime()}", snapshot)

        # Live preview (optional)
        # Comment out for headless operation
        cv2.imshow("Parking Lot Feed", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
