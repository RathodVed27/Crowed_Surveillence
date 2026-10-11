from ultralytics import YOLO
import cv2
import os
import numpy as np

# ==============================
# CONFIGURATION
# ==============================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0003.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test.jpg"

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.05
IOU_THRESHOLD = 0.45
MAX_DETECTIONS = 1000

# ==============================
# LOAD MODEL
# ==============================

print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")

# ==============================
# LOAD IMAGE
# ==============================

image = cv2.imread(SOURCE_IMAGE)

if image is None:
    raise FileNotFoundError(
        f"Cannot load image: {SOURCE_IMAGE}"
    )

height, width = image.shape[:2]

print(f"Image size: {width} x {height}")

# ==============================
# TILE SETTINGS
# ==============================

stride = TILE_SIZE - OVERLAP

all_boxes = []
all_scores = []

# ==============================
# PROCESS TILES
# ==============================

tile_number = 0

for y in range(0, height, stride):

    for x in range(0, width, stride):

        x1 = x
        y1 = y

        x2 = min(x + TILE_SIZE, width)
        y2 = min(y + TILE_SIZE, height)

        tile = image[y1:y2, x1:x2]

        if tile.size == 0:
            continue

        tile_number += 1

        print(
            f"Processing tile {tile_number}: "
            f"x={x1}:{x2}, y={y1}:{y2}"
        )

        results = model.predict(
            source=tile,
            conf=CONFIDENCE,
            iou=IOU_THRESHOLD,
            imgsz=TILE_SIZE,
            max_det=MAX_DETECTIONS,
            verbose=False,
            device=0
        )

        result = results[0]

        if result.boxes is None:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()

        # Convert tile coordinates
        # back to original image coordinates

        for box, score in zip(boxes, scores):

            bx1, by1, bx2, by2 = box

            bx1 += x1
            bx2 += x1

            by1 += y1
            by2 += y1

            all_boxes.append(
                [bx1, by1, bx2, by2]
            )

            all_scores.append(float(score))

# ==============================
# NO DETECTIONS
# ==============================

if len(all_boxes) == 0:

    print("No heads detected.")

    cv2.imwrite(
        OUTPUT_IMAGE,
        image
    )

    exit()

# ==============================
# NMS - REMOVE DUPLICATES
# ==============================

boxes_for_nms = []

for box in all_boxes:

    x1, y1, x2, y2 = box

    boxes_for_nms.append([
        int(x1),
        int(y1),
        int(x2 - x1),
        int(y2 - y1)
    ])

indices = cv2.dnn.NMSBoxes(
    boxes_for_nms,
    all_scores,
    CONFIDENCE,
    IOU_THRESHOLD
)

# ==============================
# DRAW FINAL DETECTIONS
# ==============================

final_count = 0

if len(indices) > 0:

    indices = np.array(indices).flatten()

    for i in indices:

        x1, y1, x2, y2 = all_boxes[i]

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        score = all_scores[i]

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            image,
            f"head {score:.2f}",
            (x1, max(y1 - 5, 15)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            1
        )

        final_count += 1

# ==============================
# DISPLAY COUNT
# ==============================

cv2.putText(
    image,
    f"People Count: {final_count}",
    (20, 40),
    cv2.FONT_HERSHEY_SIMPLEX,
    1,
    (0, 255, 0),
    2
)

# ==============================
# SAVE
# ==============================

os.makedirs(
    os.path.dirname(OUTPUT_IMAGE),
    exist_ok=True
)

cv2.imwrite(
    OUTPUT_IMAGE,
    image
)

print()
print("=" * 50)
print("TILED DETECTION COMPLETE")
print("=" * 50)
print(f"Tiles processed : {tile_number}")
print(f"Final head count: {final_count}")
print(f"Output image    : {OUTPUT_IMAGE}")
print("=" * 50)