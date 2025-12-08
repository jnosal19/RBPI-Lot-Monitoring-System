# main.py

import os
import time
import cv2

from camera import Camera
from detector.yolo_detector import YOLODetector
from detector.state_machine import PresenceStateMachine
from notifier.webhook_notifier import WebhookNotifier

from config import SNAPSHOT_DIR, YOLO_EVERY_N_FRAMES


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
    state_machine = PresenceStateMachine(frames_required=5)
    notifier = WebhookNotifier()

    frame_count = 0
    vehicle_present = False  # ⭐ PERSIST this variable between frames
    detections = []  # ⭐ Store last detections for visualization

    print("Parking lot monitor running... Press Ctrl+C to stop.")

    while True:
        frame = cam.read()
        frame_count += 1

        # Only run YOLO every N frames
        should_run_yolo = (frame_count % YOLO_EVERY_N_FRAMES == 0)

        if should_run_yolo:
            detections = detector.detect(frame)
            # Update vehicle_present only when we actually run YOLO
            vehicle_present = len(detections) > 0
            print(f"Frame {frame_count}: Vehicle present = {vehicle_present}")

        # Draw boxes for visualization (using last known detections)
        for det in detections:
            (x1, y1, x2, y2) = det["box"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, "vehicle", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Update state machine EVERY frame with the last known state
        event = state_machine.update(vehicle_present)

        # Trigger Discord Webhook
        if event == "ENTER":
            print(">>> VEHICLE ENTERED LOT")
            snapshot = save_snapshot(frame)
            notifier.send("Vehicle ENTERED lot", f"Time: {time.ctime()}", snapshot)

        elif event == "EXIT":
            print(">>> VEHICLE EXITED LOT")
            snapshot = save_snapshot(frame)
            notifier.send("Vehicle EXITED lot", f"Time: {time.ctime()}", snapshot)

        # Live preview window
        cv2.imshow("Parking Lot Feed", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
