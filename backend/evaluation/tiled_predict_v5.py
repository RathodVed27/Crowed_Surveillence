from ultralytics import YOLO
import cv2
import numpy as np
import os
import math


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test_v5.jpg"

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.03

MODEL_IOU = 0.50

MAX_DETECTIONS = 1000

# Maximum distance between centers for considering
# two detections duplicates.
CENTER_DISTANCE = 18


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")


# ============================================================
# LOAD IMAGE
# ============================================================

image = cv2.imread(SOURCE_IMAGE)

if image is None:
    raise FileNotFoundError(SOURCE_IMAGE)

height, width = image.shape[:2]

print(f"Image size: {width} x {height}")


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


x_starts = get_positions(width)
y_starts = get_positions(height)

print(f"X positions: {x_starts}")
print(f"Y positions: {y_starts}")


# ============================================================
# COLLECT ALL DETECTIONS
# ============================================================

detections = []

raw_count = 0


for y in y_starts:

    for x in x_starts:

        x2 = min(x + TILE_SIZE, width)
        y2 = min(y + TILE_SIZE, height)

        tile = image[y:y2, x:x2]

        print(
            f"\nTile: "
            f"x={x}:{x2}, "
            f"y={y}:{y2}"
        )

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
            print("Raw detections: 0")
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()

        print(
            f"Raw detections: {len(boxes)}"
        )

        raw_count += len(boxes)

        for box, score in zip(boxes, scores):

            bx1, by1, bx2, by2 = box

            # Convert tile coordinates
            # to original image coordinates.

            bx1 += x
            bx2 += x

            by1 += y
            by2 += y

            # Clip to image.

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

            center_x = (
                bx1 + bx2
            ) / 2

            center_y = (
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
                "cx": center_x,
                "cy": center_y
            })


# ============================================================
# RAW STATISTICS
# ============================================================

print()
print("=" * 70)

print(
    f"Raw detections: {raw_count}"
)

print(
    f"Valid detections: {len(detections)}"
)

print("=" * 70)


# ============================================================
# CENTER DISTANCE MERGING
# ============================================================

# Highest confidence detections are processed first.

detections.sort(
    key=lambda d: d["score"],
    reverse=True
)


kept = []


for detection in detections:

    cx = detection["cx"]
    cy = detection["cy"]

    is_duplicate = False

    for existing in kept:

        distance = math.sqrt(
            (cx - existing["cx"]) ** 2
            +
            (cy - existing["cy"]) ** 2
        )

        if distance <= CENTER_DISTANCE:

            is_duplicate = True
            break


    if not is_duplicate:

        kept.append(detection)


# ============================================================
# RESULT
# ============================================================

final_count = len(kept)


print(
    f"After center-distance merging: "
    f"{final_count}"
)

print(
    f"Removed as duplicates: "
    f"{len(detections) - final_count}"
)


# ============================================================
# DRAW RESULTS
# ============================================================

for detection in kept:

    x1, y1, x2, y2 = (
        detection["box"]
    )

    score = detection["score"]

    x1 = int(x1)
    y1 = int(y1)
    x2 = int(x2)
    y2 = int(y2)

    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        1
    )

    cv2.putText(
        image,
        f"{score:.2f}",
        (
            x1,
            max(12, y1 - 2)
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        (0, 255, 0),
        1
    )


# ============================================================
# COUNT TEXT
# ============================================================

cv2.putText(
    image,
    f"People Count: {final_count}",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)


# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(
        OUTPUT_IMAGE
    ),
    exist_ok=True
)

cv2.imwrite(
    OUTPUT_IMAGE,
    image
)


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 70)

print(
    f"Final head count: {final_count}"
)

print(
    f"Output image: {OUTPUT_IMAGE}"
)

print("=" * 70)

print("V5 COMPLETE")