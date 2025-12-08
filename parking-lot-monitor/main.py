# main.py - With Web Dashboard

import os
import time
import cv2
from datetime import datetime
from threading import Thread

from camera import Camera
from detector.yolo_detector import YOLODetector
from detector.vehicle_counter import VehicleCounter
from notifier.webhook_notifier import WebhookNotifier
from web_dashboard import run_dashboard, update_dashboard_state, update_frame

from config import SNAPSHOT_DIR, YOLO_EVERY_N_FRAMES


def save_snapshot(frame, vehicle_count=0):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{timestamp}_count_{vehicle_count}.jpg"
    path = os.path.join(SNAPSHOT_DIR, filename)
    cv2.imwrite(path, frame)
    return path


def draw_ui_overlay(frame, vehicle_count, fps=0):
    """Draw clean UI overlay with vehicle count and status"""
    h, w = frame.shape[:2]
    
    # Semi-transparent overlay at top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Vehicle count
    count_text = f"Vehicles: {vehicle_count}"
    cv2.putText(frame, count_text, (10, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    
    # Status indicator
    status_color = (0, 255, 0) if vehicle_count > 0 else (128, 128, 128)
    cv2.circle(frame, (w - 30, 30), 12, status_color, -1)
    
    # FPS counter
    if fps > 0:
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 120, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Timestamp
    timestamp = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, timestamp, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Dashboard URL
    cv2.putText(frame, "Dashboard: http://raspberrypi.local:5000", 
                (w - 380, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


def main():
    # Start web dashboard in background thread
    dashboard_thread = Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    print("🌐 Web Dashboard started at http://0.0.0.0:5000")
    print("   Access from any device on your network!")
    
    cam = Camera()
    cam.open()

    detector = YOLODetector()
    counter = VehicleCounter(stability_frames=5)
    notifier = WebhookNotifier()

    frame_count = 0
    detected_count = 0
    detections = []
    
    # FPS calculation
    fps_start_time = time.time()
    fps_frame_count = 0
    current_fps = 0

    print("\n🚗 Enhanced Parking Lot Monitor Running...")
    print("=" * 50)
    print("Features:")
    print("  • Multi-vehicle tracking")
    print("  • Live web dashboard")
    print("  • Real-time count display")
    print("  • Discord notifications")
    print("  • Press 'q' to quit")
    print("=" * 50)

    # Initialize dashboard state
    update_dashboard_state(0, None)

    while True:
        frame = cam.read()
        frame_count += 1
        fps_frame_count += 1

        # Calculate FPS every second
        if time.time() - fps_start_time >= 1.0:
            current_fps = fps_frame_count / (time.time() - fps_start_time)
            fps_start_time = time.time()
            fps_frame_count = 0

        # Run YOLO detection
        should_run_yolo = (frame_count % YOLO_EVERY_N_FRAMES == 0)

        if should_run_yolo:
            detections = detector.detect(frame)
            detected_count = len(detections)

        # Draw detection boxes with individual labels
        for i, det in enumerate(detections):
            (x1, y1, x2, y2) = det["box"]
            conf = det["confidence"]
            
            # Color-coded boxes (different color for each vehicle)
            colors = [(0, 255, 0), (255, 165, 0), (255, 0, 255), (0, 255, 255), (255, 255, 0)]
            color = colors[i % len(colors)]
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label with vehicle number and confidence
            label = f"Vehicle #{i+1} ({conf:.2f})"
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Update vehicle counter
        event, current_count = counter.update(detected_count)

        # Handle count changes
        if event == 'INCREASE':
            change = current_count - (current_count - 1)
            print(f"📈 Vehicle count INCREASED: {current_count-change} → {current_count}")
            snapshot = save_snapshot(frame, current_count)
            
            # Update dashboard
            update_dashboard_state(current_count, 'INCREASE')
            
            if current_count == 1:
                notifier.send(
                    "🚗 Vehicle Entered Lot",
                    f"Count: {current_count}\nTime: {time.ctime()}",
                    snapshot
                )
            else:
                notifier.send(
                    "🚗 Additional Vehicle Detected",
                    f"Total vehicles: {current_count}\nTime: {time.ctime()}",
                    snapshot
                )

        elif event == 'DECREASE':
            change = (current_count + 1) - current_count
            print(f"📉 Vehicle count DECREASED: {current_count+change} → {current_count}")
            snapshot = save_snapshot(frame, current_count)
            
            # Update dashboard
            update_dashboard_state(current_count, 'DECREASE')
            
            if current_count == 0:
                notifier.send(
                    "🚦 Parking Lot Empty",
                    f"Last vehicle departed\nTime: {time.ctime()}",
                    snapshot
                )
            else:
                notifier.send(
                    "👋 Vehicle Departed",
                    f"Remaining vehicles: {current_count}\nTime: {time.ctime()}",
                    snapshot
                )

        # Draw UI overlay
        draw_ui_overlay(frame, current_count, current_fps)
        
        # Update dashboard with latest frame
        update_frame(frame)
        
        # Update dashboard state regularly (even without events)
        if frame_count % 30 == 0:  # Every 30 frames
            update_dashboard_state(current_count, None)

        # Display local preview
        cv2.imshow("Parking Lot Monitor", frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
    print("\n✓ Monitor stopped")


if __name__ == "__main__":
    main()
