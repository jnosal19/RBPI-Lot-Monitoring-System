# config.py

# YOLO model to use (nano version)
YOLO_MODEL_PATH = "yolov8n.pt"

# Run YOLO every N frames (Optimization)
YOLO_EVERY_N_FRAMES = 3

# Camera settings
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Parking lot ROI (x, y, w, h)
# Placeholder – fill these in later based on applicable camera view
ROI = (0, 0, 640, 480)

# Vehicle classes we care about (COCO dataset indices)
VEHICLE_CLASSES = {2, 5, 7}  # car, bus, truck

# Stability settings
FRAMES_REQUIRED_INSIDE = 1
FRAMES_REQUIRED_OUTSIDE = 1

# Snapshot & log directories
SNAPSHOT_DIR = "data/snapshots"
LOG_DIR = "data/logs"

# Notification settings
WEBHOOK_URL = "https://discord.com/api/webhooks/1447627923023462604/vJPA0Tf9ClhhbIKBdH-NxP7oW8AtCFMMhdZrqXHaomOq6VXNxkuLPPmrlYYU85U5so3a"  # <-- fill this in with your Discord or Slack webhook URL
