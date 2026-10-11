from ultralytics import YOLO
import cv2
import os
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0003.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test_v2.jpg"

TILE_SIZE = 512
OVERLAP = 128

# Detection settings
CONFIDENCE = 0.10
MODEL_IOU = 0.50
MAX_DETECTIONS = 1000

# Final duplicate-removal settings
FINAL_IOU = 0.30


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
    raise FileNotFoundError(
        f"Cannot load image: {SOURCE_IMAGE}"
    )

height, width = image.shape[:2]

print(f"Image size: {width} x {height}")


# ============================================================
# TILE START POSITIONS
# ============================================================

stride = TILE_SIZE - OVERLAP

x_starts = list(range(0, width, stride))
y_starts = list(range(0, height, stride))

print(f"X tile starts: {x_starts}")
print(f"Y tile starts: {y_starts}")


# ============================================================
# STORAGE
# ============================================================

all_boxes = []
all_scores = []

tile_number = 0


# ============================================================
# PROCESS TILES
# ============================================================

for y_index, y in enumerate(y_starts):

    for x_index, x in enumerate(x_starts):

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

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        results = model.predict(
            source=tile,
            conf=CONFIDENCE,
            iou=MODEL_IOU,
            imgsz=TILE_SIZE,
            max_det=MAX_DETECTIONS,
            verbose=False,
            device=0
        )

        result = results[0]

        if result.boxes is None or len(result.boxes) == 0:
            print("   -> 0 detections")
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()

        print(f"   -> {len(boxes)} raw detections")

        # ----------------------------------------------------
        # TILE OWNERSHIP
        #
        # Only keep detections whose CENTER belongs to this
        # tile's unique region.
        #
        # This prevents duplicate detections caused by overlap.
        # ----------------------------------------------------

        # Determine ownership boundaries in X
        if x_index == 0:
            owner_x1 = 0
        else:
            previous_x = x_starts[x_index - 1]
            owner_x1 = (previous_x + x) // 2

        if x_index == len(x_starts) - 1:
            owner_x2 = width
        else:
            next_x = x_starts[x_index + 1]
            owner_x2 = (x + next_x) // 2

        # Determine ownership boundaries in Y
        if y_index == 0:
            owner_y1 = 0
        else:
            previous_y = y_starts[y_index - 1]
            owner_y1 = (previous_y + y) // 2

        if y_index == len(y_starts) - 1:
            owner_y2 = height
        else:
            next_y = y_starts[y_index + 1]
            owner_y2 = (y + next_y) // 2

        kept = 0

        for box, score in zip(boxes, scores):

            bx1, by1, bx2, by2 = box

            # Convert tile coordinates -> original image
            bx1 += x1
            bx2 += x1

            by1 += y1
            by2 += y1

            # Center of detection
            center_x = (bx1 + bx2) / 2
            center_y = (by1 + by2) / 2

            # Keep detection only if its center belongs
            # to this tile's ownership region.
            if not (
                owner_x1 <= center_x < owner_x2
                and
                owner_y1 <= center_y < owner_y2
            ):
                continue

            all_boxes.append(
                [bx1, by1, bx2, by2]
            )

            all_scores.append(float(score))

            kept += 1

        print(f"   -> {kept} kept after tile ownership")


# ============================================================
# CHECK DETECTIONS
# ============================================================

print()
print("=" * 60)

if len(all_boxes) == 0:

    print("NO DETECTIONS FOUND")
    print("=" * 60)

    cv2.imwrite(OUTPUT_IMAGE, image)

    exit()


print(f"Detections before final NMS: {len(all_boxes)}")


# ============================================================
# FINAL NMS
# ============================================================

boxes_for_nms = []

for box in all_boxes:

    x1, y1, x2, y2 = box

    boxes_for_nms.append(
        [
            int(x1),
            int(y1),
            int(x2 - x1),
            int(y2 - y1)
        ]
    )


indices = cv2.dnn.NMSBoxes(
    boxes_for_nms,
    all_scores,
    CONFIDENCE,
    FINAL_IOU
)


# ============================================================
# DRAW FINAL DETECTIONS
# ============================================================

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
            1
        )

        cv2.putText(
            image,
            f"{score:.2f}",
            (x1, max(y1 - 3, 12)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 255, 0),
            1
        )

        final_count += 1


# ============================================================
# DISPLAY COUNT
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
# FINAL RESULT
# ============================================================

print(f"Final head count: {final_count}")
print(f"Output image: {OUTPUT_IMAGE}")

print("=" * 60)
print("TILED DETECTION V2 COMPLETE")
print("=" * 60)