from ultralytics import YOLO
import cv2
import numpy as np
import os


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

SOURCE_IMAGE = r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images\0007.jpg"

OUTPUT_IMAGE = r"F:\Crowed_Surveillence\runs\tiled_test_v4.jpg"

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.03

MODEL_IOU = 0.50

MAX_DETECTIONS = 1000

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
# CREATE CLEAN TILE POSITIONS
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
# STORE DETECTIONS
# ============================================================

all_boxes = []
all_scores = []

owned_boxes = []
owned_scores = []

raw_count = 0
owned_count = 0


# ============================================================
# PROCESS TILES
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

        raw_count += len(boxes)


        # ====================================================
        # TILE CORE / OWNERSHIP REGION
        # ====================================================
        #
        # Each tile owns its central region.
        # This prevents the same head from being counted
        # once in every overlapping tile.
        #

        if len(x_starts) == 1:

            core_x1 = 0
            core_x2 = width

        elif x == x_starts[0]:

            core_x1 = 0
            core_x2 = (
                x + TILE_SIZE - OVERLAP // 2
            )

        elif x == x_starts[-1]:

            core_x1 = (
                x + OVERLAP // 2
            )
            core_x2 = width

        else:

            core_x1 = (
                x + OVERLAP // 2
            )

            core_x2 = (
                x + TILE_SIZE - OVERLAP // 2
            )


        if len(y_starts) == 1:

            core_y1 = 0
            core_y2 = height

        elif y == y_starts[0]:

            core_y1 = 0
            core_y2 = (
                y + TILE_SIZE - OVERLAP // 2
            )

        elif y == y_starts[-1]:

            core_y1 = (
                y + OVERLAP // 2
            )
            core_y2 = height

        else:

            core_y1 = (
                y + OVERLAP // 2
            )

            core_y2 = (
                y + TILE_SIZE - OVERLAP // 2
            )


        # ====================================================
        # CONVERT BOXES TO ORIGINAL IMAGE
        # ====================================================

        for box, score in zip(boxes, scores):

            bx1, by1, bx2, by2 = box

            bx1 += x
            bx2 += x

            by1 += y
            by2 += y


            # Clip to original image

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


            all_boxes.append(
                [bx1, by1, bx2, by2]
            )

            all_scores.append(
                float(score)
            )


            # =================================================
            # CENTER OWNERSHIP
            # =================================================

            center_x = (
                (bx1 + bx2) / 2
            )

            center_y = (
                (by1 + by2) / 2
            )


            belongs_to_tile = (
                core_x1 <= center_x < core_x2
                and
                core_y1 <= center_y < core_y2
            )


            if belongs_to_tile:

                owned_boxes.append(
                    [bx1, by1, bx2, by2]
                )

                owned_scores.append(
                    float(score)
                )

                owned_count += 1


# ============================================================
# STATISTICS
# ============================================================

print()
print("=" * 70)

print(
    f"Total raw detections     : {raw_count}"
)

print(
    f"Center-owned detections  : {owned_count}"
)

print("=" * 70)


# ============================================================
# CHOOSE OWNED DETECTIONS
# ============================================================

if len(owned_boxes) == 0:

    print("No owned detections.")

    cv2.imwrite(
        OUTPUT_IMAGE,
        image
    )

    raise SystemExit


# ============================================================
# FINAL NMS
# ============================================================

nms_boxes = []

for box in owned_boxes:

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
    owned_scores,
    CONFIDENCE,
    FINAL_IOU
)


# ============================================================
# DRAW FINAL DETECTIONS
# ============================================================

final_count = 0

if len(indices) > 0:

    indices = np.array(
        indices
    ).flatten()

    for index in indices:

        x1, y1, x2, y2 = (
            owned_boxes[index]
        )

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        score = owned_scores[index]


        # Draw box

        cv2.rectangle(
            image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            1
        )


        # Draw confidence

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


        final_count += 1


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
# SAVE IMAGE
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
# FINAL RESULT
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

print("V4 COMPLETE")