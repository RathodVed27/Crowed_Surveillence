from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path
import math


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

IMAGE_DIR = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images"
)

GT_DIR = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\gt"
)

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.03
MODEL_IOU = 0.50
MAX_DETECTIONS = 1000

CENTER_DISTANCES = [
    10,
    12,
    15,
    18,
    20,
    25,
    30
]

TEST_IMAGES = [
    "0003.jpg",
    "0007.jpg",
    "0009.jpg",
    "0011.jpg",
    "0013.jpg",
    "0042.jpg",
    "0056.jpg",
    "0058.jpg",
    "0068.jpg",
    "0070.jpg"
]


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")
print()


# ============================================================
# TILE POSITIONS
# ============================================================

def get_positions(length):

    if length <= TILE_SIZE:
        return [0]

    stride = TILE_SIZE - OVERLAP

    positions = []
    position = 0

    while position + TILE_SIZE < length:

        positions.append(position)

        position += stride

    last_position = length - TILE_SIZE

    if last_position not in positions:
        positions.append(last_position)

    return positions


# ============================================================
# GET GROUND TRUTH
# ============================================================

def get_ground_truth(path):

    if not path.exists():
        return 0

    with open(path, "r", encoding="utf-8") as f:

        lines = [
            line.strip()
            for line in f
            if line.strip()
        ]

    return len(lines)


# ============================================================
# COLLECT DETECTIONS
# ============================================================

def collect_detections(image):

    height, width = image.shape[:2]

    x_starts = get_positions(width)
    y_starts = get_positions(height)

    detections = []

    raw_count = 0

    for y in y_starts:

        for x in x_starts:

            x2 = min(
                x + TILE_SIZE,
                width
            )

            y2 = min(
                y + TILE_SIZE,
                height
            )

            tile = image[y:y2, x:x2]

            results = model.predict(
                source=tile,
                conf=CONFIDENCE,
                iou=MODEL_IOU,
                imgsz=TILE_SIZE,
                max_det=MAX_DETECTIONS,
                device=0,
                verbose=False
            )

            result = results[0]

            if result.boxes is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()

            raw_count += len(boxes)

            for box, score in zip(boxes, scores):

                bx1, by1, bx2, by2 = box

                bx1 += x
                bx2 += x

                by1 += y
                by2 += y

                bx1 = max(
                    0,
                    min(width, bx1)
                )

                bx2 = max(
                    0,
                    min(width, bx2)
                )

                by1 = max(
                    0,
                    min(height, by1)
                )

                by2 = max(
                    0,
                    min(height, by2)
                )

                if bx2 <= bx1 or by2 <= by1:
                    continue

                cx = (
                    bx1 + bx2
                ) / 2

                cy = (
                    by1 + by2
                ) / 2

                detections.append({
                    "box": [
                        bx1,
                        by1,
                        bx2,
                        by2
                    ],
                    "score": float(score),
                    "cx": cx,
                    "cy": cy
                })

    return detections, raw_count


# ============================================================
# CENTER DISTANCE MERGING
# ============================================================

def merge_detections(
    detections,
    center_distance
):

    # Highest confidence first.

    detections = sorted(
        detections,
        key=lambda d: d["score"],
        reverse=True
    )

    kept = []

    for detection in detections:

        duplicate = False

        cx = detection["cx"]
        cy = detection["cy"]

        for existing in kept:

            distance = math.sqrt(
                (cx - existing["cx"]) ** 2
                +
                (cy - existing["cy"]) ** 2
            )

            if distance <= center_distance:

                duplicate = True
                break

        if not duplicate:

            kept.append(detection)

    return len(kept)


# ============================================================
# MAIN EVALUATION
# ============================================================

all_detections = {}

print("=" * 80)
print("COLLECTING DETECTIONS")
print("=" * 80)

for image_name in TEST_IMAGES:

    image_path = IMAGE_DIR / image_name
    gt_path = GT_DIR / f"{image_path.stem}.txt"

    image = cv2.imread(
        str(image_path)
    )

    if image is None:
        print(
            f"Could not read {image_name}"
        )
        continue

    ground_truth = get_ground_truth(
        gt_path
    )

    print(
        f"{image_name} | GT = {ground_truth}"
    )

    detections, raw_count = collect_detections(
        image
    )

    all_detections[image_name] = (
        ground_truth,
        detections
    )

    print(
        f"  Raw detections = {raw_count}"
    )


# ============================================================
# TEST CENTER DISTANCES
# ============================================================

print()
print("=" * 80)
print("CENTER DISTANCE COMPARISON")
print("=" * 80)

for distance in CENTER_DISTANCES:

    errors = []
    percentage_errors = []

    print()
    print(
        f"CENTER DISTANCE = {distance}px"
    )

    print("-" * 80)

    for image_name, data in all_detections.items():

        ground_truth, detections = data

        predicted = merge_detections(
            detections,
            distance
        )

        error = abs(
            predicted - ground_truth
        )

        if ground_truth > 0:

            percentage_error = (
                error / ground_truth
            ) * 100

        else:

            percentage_error = 0

        errors.append(error)
        percentage_errors.append(
            percentage_error
        )

        print(
            f"{image_name:10s} | "
            f"GT={ground_truth:5d} | "
            f"Pred={predicted:5d} | "
            f"Error={error:5d} | "
            f"Error%={percentage_error:7.2f}%"
        )

    mae = np.mean(errors)

    mape = np.mean(
        percentage_errors
    )

    rmse = math.sqrt(
        np.mean(
            np.array(errors) ** 2
        )
    )

    print("-" * 80)

    print(
        f"MAE={mae:.2f} | "
        f"RMSE={rmse:.2f} | "
        f"MAPE={mape:.2f}%"
    )


# ============================================================
# COMPLETE
# ============================================================

print()
print("=" * 80)
print("TUNING COMPLETE")
print("=" * 80)