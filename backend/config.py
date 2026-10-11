"""
Crowd Surveillance Configuration
Author: Ved Rathod
"""

from pathlib import Path

# ---------------------------------------------------
# Project Paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "models"

DATABASE_DIR = BASE_DIR / "database"

LOG_DIR = BASE_DIR / "logs"

# ---------------------------------------------------
# YOLO
# ---------------------------------------------------

# Trained head-detection model (use this after training)
TRAINED_MODEL = MODEL_DIR / "crowd_head_model.pt"

# Fallback to generic YOLO if trained model not available
DEFAULT_MODEL = MODEL_DIR / "yolov8n.pt"

# Automatically use trained model if it exists
if TRAINED_MODEL.exists():
    YOLO_MODEL = TRAINED_MODEL
    USE_HEAD_DETECTION = True
    print(f"[CONFIG] Using trained head detection model: {TRAINED_MODEL.name}")
else:
    YOLO_MODEL = DEFAULT_MODEL
    USE_HEAD_DETECTION = False
    print(f"[CONFIG] Trained model not found, using default: {DEFAULT_MODEL.name}")

CONFIDENCE = 0.35  # Lower confidence for better recall in dense crowds

# Class IDs
PERSON_CLASS = 0   # Class 0 = 'person' in default COCO model
HEAD_CLASS = 0     # Class 0 = 'head' in our trained model

# ---------------------------------------------------
# Camera
# ---------------------------------------------------

CAMERA_INDEX = 0

FRAME_WIDTH = 1280

FRAME_HEIGHT = 720

FPS = 30

# ---------------------------------------------------
# Serial Communication
# ---------------------------------------------------

SERIAL_PORT = "COM3"

BAUD_RATE = 115200

SERIAL_TIMEOUT = 1

# ---------------------------------------------------
# Crowd Thresholds
# ---------------------------------------------------

LOW_CROWD = 5

MEDIUM_CROWD = 15

HIGH_CROWD = 30

# ---------------------------------------------------
# Piezo Threshold
# ---------------------------------------------------

PIEZO_THRESHOLD = 100

# ---------------------------------------------------
# Database
# ---------------------------------------------------

DATABASE_FILE = DATABASE_DIR / "crowd.db"