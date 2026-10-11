import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
from math import sqrt


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = Path(
    r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"
)

IMAGE_PATH = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"
)

OUTPUT_PATH = Path(
    r"F:\Crowed_Surveillence\runs\v7_0007.jpg"
)

TILE_SIZE = 512
OVERLAP = 128
STRIDE = TILE_SIZE - OVERLAP

CONFIDENCE = 0.03
IOU_MODEL = 0.50
MAX_DET = 1000

# V7 duplicate rules
DUPLICATE_IOU = 0.15
CENTER_DISTANCE_RATIO = 0.50


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(str(MODEL_PATH))

print("Model loaded.")


# ============================================================
# IOU FUNCTION
# ============================================================

def calculate_iou(box1, box2):
    """
    Calculate IoU between two boxes.

    Box format:
    [x1, y1, x2, y2]
    """

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection_width = max(0, x2 - x1)
    intersection_height = max(0, y2 - y1)

    intersection = intersection_width * intersection_height

    area1 = max(0, box1[2] - box1[0]) * max(
        0, box1[3] - box1[1]
    )

    area2 = max(0, box2[2] - box2[0]) * max(
        0, box2[3] - box2[1]
    )

    union = area1 + area2 - intersection

    if union <= 0:
        return 0.0

    return intersection / union


# ============================================================
# CENTER DISTANCE
# ============================================================

def center_distance(box1, box2):

    c1x = (box1[0] + box1[2]) / 2
    c1y = (box1[1] + box1[3]) / 2

    c2x = (box2[0] + box2[2]) / 2
    c2y = (box2[1] + box2[3]) / 2

    return sqrt(
        (c1x - c2x) ** 2 +
        (c1y - c2y) ** 2
    )


# ============================================================
# TILE OVERLAP CHECK
# ============================================================

def tiles_overlap(tile1, tile2):

    x1, y1, x2, y2 = tile1
    a1, b1, a2, b2 = tile2

    return not (
        x2 <= a1 or
        a2 <= x1 or
        y2 <= b1 or
        b2 <= y1
    )


# ============================================================
# DUPLICATE CHECK
# ============================================================

def is_duplicate(det_a, det_b):

    # IMPORTANT:
    # Only compare detections coming from different tiles.

    if det_a["tile_id"] == det_b["tile_id"]:
        return False

    # Their tiles must actually overlap.
    if not tiles_overlap(
        det_a["tile"],
        det_b["tile"]
    ):
        return False

    box_a = det_a["box"]
    box_b = det_b["box"]

    iou = calculate_iou(box_a, box_b)

    distance = center_distance(
        box_a,
        box_b
    )

    width_a = box_a[2] - box_a[0]
    height_a = box_a[3] - box_a[1]

    width_b = box_b[2] - box_b[0]
    height_b = box_b[3] - box_b[1]

    size_a = max(width_a, height_a)
    size_b = max(width_b, height_b)

    reference_size = min(size_a, size_b)

    if reference_size <= 0:
        return False

    # Center distance must also be small.
    center_limit = (
        reference_size *
        CENTER_DISTANCE_RATIO
    )

    # V7 requires BOTH:
    #
    # 1. Some box overlap
    # 2. Very close centers
    #
    # This prevents two nearby real heads
    # from being merged too easily.

    if (
        iou >= DUPLICATE_IOU
        and distance <= center_limit
    ):
        return True

    return False


# ============================================================
# READ IMAGE
# ============================================================

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(
        f"Could not read image:\n{IMAGE_PATH}"
    )

original = image.copy()

height, width = image.shape[:2]

print()
print("Image size:")
print(f"Width  : {width}")
print(f"Height : {height}")


# ============================================================
# CREATE TILE POSITIONS
# ============================================================

x_positions = list(range(0, width - TILE_SIZE + 1, STRIDE))
y_positions = list(range(0, height - TILE_SIZE + 1, STRIDE))

# Make sure the right/bottom edge is covered.
if x_positions[-1] != width - TILE_SIZE:
    x_positions.append(width - TILE_SIZE)

if y_positions[-1] != height - TILE_SIZE:
    y_positions.append(height - TILE_SIZE)


# Remove duplicates and sort.
x_positions = sorted(set(x_positions))
y_positions = sorted(set(y_positions))


print()
print(f"Tiles X: {len(x_positions)}")
print(f"Tiles Y: {len(y_positions)}")
print(f"Total tiles: {len(x_positions) * len(y_positions)}")


# ============================================================
# DETECTIONS
# ============================================================

detections = []

tile_id = 0


# ============================================================
# RUN YOLO ON EACH TILE
# ============================================================

for y in y_positions:

    for x in x_positions:

        tile_id += 1

        x2 = min(
            x + TILE_SIZE,
            width
        )

        y2 = min(
            y + TILE_SIZE,
            height
        )

        tile = original[y:y2, x:x2]

        results = model.predict(
            source=tile,
            conf=CONFIDENCE,
            iou=IOU_MODEL,
            max_det=MAX_DET,
            verbose=False,
            device=0
        )

        result = results[0]

        if result.boxes is None:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()

        for box, score, cls in zip(
            boxes,
            scores,
            classes
        ):

            # We are detecting heads,
            # so keep class 0.
            if int(cls) != 0:
                continue

            bx1, by1, bx2, by2 = box

            # Convert tile coordinates
            # to original image coordinates.
            gx1 = bx1 + x
            gy1 = by1 + y
            gx2 = bx2 + x
            gy2 = by2 + y

            detections.append({
                "box": [
                    float(gx1),
                    float(gy1),
                    float(gx2),
                    float(gy2)
                ],
                "confidence": float(score),
                "tile_id": tile_id,
                "tile": [
                    x,
                    y,
                    x2,
                    y2
                ]
            })


# ============================================================
# RAW COUNT
# ============================================================

raw_count = len(detections)

print()
print("==============================")
print(f"RAW DETECTIONS: {raw_count}")
print("==============================")


# ============================================================
# SORT BY CONFIDENCE
# ============================================================

detections.sort(
    key=lambda d: d["confidence"],
    reverse=True
)


# ============================================================
# V7 DUPLICATE REMOVAL
# ============================================================

kept = []

removed = []

for current in detections:

    duplicate_found = False

    duplicate_index = -1

    for i, existing in enumerate(kept):

        if is_duplicate(
            current,
            existing
        ):

            duplicate_found = True
            duplicate_index = i
            break

    if not duplicate_found:

        kept.append(current)

    else:

        # Keep the higher-confidence detection.
        existing = kept[duplicate_index]

        if (
            current["confidence"]
            > existing["confidence"]
        ):

            kept[duplicate_index] = current

            removed.append(existing)

        else:

            removed.append(current)


# ============================================================
# FINAL COUNT
# ============================================================

final_count = len(kept)

removed_count = len(removed)


print()
print("==============================")
print("V7 RESULTS")
print("==============================")

print(f"Raw detections     : {raw_count}")
print(f"Duplicates removed : {removed_count}")
print(f"Final detections   : {final_count}")


# ============================================================
# DRAW FINAL DETECTIONS
# ============================================================

output = original.copy()

for index, detection in enumerate(kept):

    x1, y1, x2, y2 = map(
        int,
        detection["box"]
    )

    confidence = detection["confidence"]

    cv2.rectangle(
        output,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    cv2.putText(
        output,
        f"{confidence:.2f}",
        (x1, max(15, y1 - 5)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (0, 255, 0),
        1
    )


# ============================================================
# ADD INFORMATION
# ============================================================

cv2.putText(
    output,
    f"Raw detections: {raw_count}",
    (20, 35),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 255, 0),
    2
)

cv2.putText(
    output,
    f"V7 final count: {final_count}",
    (20, 70),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 255, 0),
    2
)

cv2.putText(
    output,
    f"Removed: {removed_count}",
    (20, 105),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.9,
    (0, 255, 0),
    2
)


# ============================================================
# SAVE
# ============================================================

cv2.imwrite(
    str(OUTPUT_PATH),
    output
)

print()
print(f"Output saved to:")
print(OUTPUT_PATH)