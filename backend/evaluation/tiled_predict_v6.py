from ultralytics import YOLO
import cv2
import numpy as np
import os


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test_v6.jpg"

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.03

MODEL_IOU = 0.50

MAX_DETECTIONS = 1000

# Duplicate IoU used ONLY for detections
# that came from overlapping tiles.
DUPLICATE_IOU = 0.30


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
# TILE OVERLAP CHECK
# ============================================================

def tiles_overlap(tile_a, tile_b):

    ax1 = tile_a["x1"]
    ay1 = tile_a["y1"]
    ax2 = tile_a["x2"]
    ay2 = tile_a["y2"]

    bx1 = tile_b["x1"]
    by1 = tile_b["y1"]
    bx2 = tile_b["x2"]
    by2 = tile_b["y2"]

    overlap_x = max(
        0,
        min(ax2, bx2) - max(ax1, bx1)
    )

    overlap_y = max(
        0,
        min(ay2, by2) - max(ay1, by1)
    )

    return (
        overlap_x > 0
        and
        overlap_y > 0
    )


# ============================================================
# BOX IOU
# ============================================================

def calculate_iou(box_a, box_b):

    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)

    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_width = max(
        0,
        inter_x2 - inter_x1
    )

    inter_height = max(
        0,
        inter_y2 - inter_y1
    )

    intersection = (
        inter_width *
        inter_height
    )

    area_a = (
        max(0, ax2 - ax1) *
        max(0, ay2 - ay1)
    )

    area_b = (
        max(0, bx2 - bx1) *
        max(0, by2 - by1)
    )

    union = (
        area_a +
        area_b -
        intersection
    )

    if union <= 0:
        return 0.0

    return intersection / union


# ============================================================
# DETECTION STORAGE
# ============================================================

detections = []

raw_count = 0

tile_id = 0


# ============================================================
# RUN YOLO ON TILES
# ============================================================

for y in y_starts:

    for x in x_starts:

        tile_id += 1

        x2 = min(
            x + TILE_SIZE,
            width
        )

        y2 = min(
            y + TILE_SIZE,
            height
        )

        tile = image[
            y:y2,
            x:x2
        ]

        print(
            f"\nTile {tile_id}: "
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

        boxes = (
            result.boxes.xyxy
            .cpu()
            .numpy()
        )

        scores = (
            result.boxes.conf
            .cpu()
            .numpy()
        )

        print(
            f"Raw detections: "
            f"{len(boxes)}"
        )

        raw_count += len(boxes)


        # ====================================================
        # SAVE DETECTIONS
        # ====================================================

        for box, score in zip(
            boxes,
            scores
        ):

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


            detections.append({

                "box": [
                    bx1,
                    by1,
                    bx2,
                    by2
                ],

                "score": float(score),

                "tile": {
                    "id": tile_id,
                    "x1": x,
                    "y1": y,
                    "x2": x2,
                    "y2": y2
                }

            })


# ============================================================
# RAW STATISTICS
# ============================================================

print()
print("=" * 70)

print(
    f"Total raw detections: "
    f"{raw_count}"
)

print(
    f"Valid detections: "
    f"{len(detections)}"
)

print("=" * 70)


# ============================================================
# SORT BY CONFIDENCE
# ============================================================

detections.sort(
    key=lambda d: d["score"],
    reverse=True
)


# ============================================================
# TILE-AWARE DUPLICATE REMOVAL
# ============================================================

kept = []

removed_duplicates = 0


for detection in detections:

    duplicate = False


    for existing in kept:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Only compare detections that came from overlapping
        # tiles.
        # ----------------------------------------------------

        if not tiles_overlap(
            detection["tile"],
            existing["tile"]
        ):

            continue


        # ----------------------------------------------------
        # Compare bounding boxes.
        # ----------------------------------------------------

        iou = calculate_iou(
            detection["box"],
            existing["box"]
        )


        if iou >= DUPLICATE_IOU:

            duplicate = True

            removed_duplicates += 1

            break


    if not duplicate:

        kept.append(
            detection
        )


# ============================================================
# FINAL COUNT
# ============================================================

final_count = len(kept)


print()
print("=" * 70)

print(
    f"Raw detections       : "
    f"{len(detections)}"
)

print(
    f"Removed duplicates   : "
    f"{removed_duplicates}"
)

print(
    f"Final detections     : "
    f"{final_count}"
)

print("=" * 70)


# ============================================================
# DRAW FINAL DETECTIONS
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
            max(
                12,
                y1 - 2
            )
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.30,
        (0, 255, 0),
        1
    )


# ============================================================
# DRAW COUNT
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
# SAVE OUTPUT
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
print(
    f"Output image: "
    f"{OUTPUT_IMAGE}"
)

print()
print("=" * 70)
print("V6 COMPLETE")
print("=" * 70)