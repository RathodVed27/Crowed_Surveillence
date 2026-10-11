from ultralytics import YOLO
import cv2
import numpy as np
import os

# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test_v3.jpg"

TILE_SIZE = 512
OVERLAP = 128

# Detection threshold
CONFIDENCE = 0.01

# YOLO's internal NMS
MODEL_IOU = 0.50

# Allow many detections in a dense crowd
MAX_DETECTIONS = 1000

# Final duplicate-removal threshold
FINAL_IOU = 0.50


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

stride = TILE_SIZE - OVERLAP

x_starts = list(range(0, width, stride))
y_starts = list(range(0, height, stride))

print(f"X positions: {x_starts}")
print(f"Y positions: {y_starts}")


# ============================================================
# STORE ALL DETECTIONS
# ============================================================

all_boxes = []
all_scores = []


# ============================================================
# PROCESS EACH TILE
# ============================================================

tile_number = 0

for y in y_starts:

    for x in x_starts:

        tile_number += 1

        x1 = x
        y1 = y

        x2 = min(x + TILE_SIZE, width)
        y2 = min(y + TILE_SIZE, height)

        tile = image[y1:y2, x1:x2]

        print(
            f"\nTile {tile_number}: "
            f"x={x1}:{x2}, y={y1}:{y2}"
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

        if result.boxes is None or len(result.boxes) == 0:

            print("Raw detections: 0")

            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()

        print(f"Raw detections: {len(boxes)}")

        # ----------------------------------------------------
        # Convert tile coordinates to original image
        # ----------------------------------------------------

        for box, score in zip(boxes, scores):

            bx1, by1, bx2, by2 = box

            bx1 += x1
            bx2 += x1

            by1 += y1
            by2 += y1

            # Clip to original image
            bx1 = max(0, min(width, bx1))
            bx2 = max(0, min(width, bx2))

            by1 = max(0, min(height, by1))
            by2 = max(0, min(height, by2))

            if bx2 <= bx1 or by2 <= by1:
                continue

            all_boxes.append(
                [bx1, by1, bx2, by2]
            )

            all_scores.append(float(score))


# ============================================================
# BEFORE NMS
# ============================================================

print("\n" + "=" * 60)

print(
    f"Total detections before merging: {len(all_boxes)}"
)


if len(all_boxes) == 0:

    print("NO DETECTIONS")

    cv2.imwrite(OUTPUT_IMAGE, image)

    raise SystemExit


# ============================================================
# CUSTOM NMS
# ============================================================

# OpenCV expects:
# [x, y, width, height]

nms_boxes = []

for box in all_boxes:

    x1, y1, x2, y2 = box

    nms_boxes.append(
        [
            int(x1),
            int(y1),
            int(x2 - x1),
            int(y2 - y1)
        ]
    )


indices = cv2.dnn.NMSBoxes(
    nms_boxes,
    all_scores,
    CONFIDENCE,
    FINAL_IOU
)


# ============================================================
# DRAW
# ============================================================

final_count = 0

if len(indices) > 0:

    indices = np.array(indices).flatten()

    for index in indices:

        x1, y1, x2, y2 = all_boxes[index]

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        score = all_scores[index]

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
            (x1, max(12, y1 - 2)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.30,
            (0, 255, 0),
            1
        )

        final_count += 1


# ============================================================
# COUNT
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
    os.path.dirname(OUTPUT_IMAGE),
    exist_ok=True
)

cv2.imwrite(
    OUTPUT_IMAGE,
    image
)


# ============================================================
# RESULT
# ============================================================

print(f"Final head count: {final_count}")

print(
    f"Output image: {OUTPUT_IMAGE}"
)

print("=" * 60)
print("V3 COMPLETE")
print("=" * 60)