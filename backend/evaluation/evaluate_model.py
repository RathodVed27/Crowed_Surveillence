from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO
import csv
import math


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"

IMAGE_DIR = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images"
)

GT_DIR = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\gt"
)

OUTPUT_CSV = Path(
    r"F:\Crowed_Surveillence\runs\crowd_evaluation.csv"
)

TILE_SIZE = 512
OVERLAP = 128

CONFIDENCE = 0.06
IOU_THRESHOLD = 0.50
MAX_DET = 1000

DEVICE = 0


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")
print()


# ============================================================
# GET GROUND TRUTH COUNT
# ============================================================

def get_ground_truth(gt_file):

    if not gt_file.exists():
        return 0

    with open(gt_file, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f
            if line.strip()
        ]

    return len(lines)


# ============================================================
# GENERATE TILES
# ============================================================

def generate_tiles(image):

    height, width = image.shape[:2]

    stride = TILE_SIZE - OVERLAP

    tiles = []

    y_positions = list(range(0, max(height - TILE_SIZE, 0) + 1, stride))
    x_positions = list(range(0, max(width - TILE_SIZE, 0) + 1, stride))

    if y_positions[-1] != max(height - TILE_SIZE, 0):
        y_positions.append(max(height - TILE_SIZE, 0))

    if x_positions[-1] != max(width - TILE_SIZE, 0):
        x_positions.append(max(width - TILE_SIZE, 0))

    for y in y_positions:

        for x in x_positions:

            tile = image[
                y:y + TILE_SIZE,
                x:x + TILE_SIZE
            ]

            tiles.append((tile, x, y))

    return tiles


# ============================================================
# GLOBAL NMS
# ============================================================

def apply_global_nms(boxes, scores):

    if len(boxes) == 0:
        return []

    boxes_for_nms = []

    for box in boxes:

        x1, y1, x2, y2 = box

        boxes_for_nms.append([
            float(x1),
            float(y1),
            float(x2 - x1),
            float(y2 - y1)
        ])

    indices = cv2.dnn.NMSBoxes(
        boxes_for_nms,
        scores,
        CONFIDENCE,
        IOU_THRESHOLD
    )

    if len(indices) == 0:
        return []

    indices = np.array(indices).reshape(-1)

    return indices.tolist()


# ============================================================
# PREDICT ONE IMAGE
# ============================================================

def predict_count(image):

    tiles = generate_tiles(image)

    all_boxes = []
    all_scores = []

    for tile, offset_x, offset_y in tiles:

        results = model.predict(
            source=tile,
            conf=CONFIDENCE,
            iou=IOU_THRESHOLD,
            max_det=MAX_DET,
            verbose=False,
            device=DEVICE
        )

        result = results[0]

        if result.boxes is None:
            continue

        boxes = result.boxes.xyxy.cpu().numpy()
        scores = result.boxes.conf.cpu().numpy()

        for box, score in zip(boxes, scores):

            x1, y1, x2, y2 = box

            x1 += offset_x
            x2 += offset_x
            y1 += offset_y
            y2 += offset_y

            all_boxes.append([
                x1,
                y1,
                x2,
                y2
            ])

            all_scores.append(float(score))

    keep = apply_global_nms(
        all_boxes,
        all_scores
    )

    return len(keep)


# ============================================================
# SELECT TEST IMAGES
# ============================================================

image_files = sorted(
    IMAGE_DIR.glob("*.jpg")
)

print("Total available images:", len(image_files))
print()

# Use first 100 images for the first evaluation.
# We can increase this later.
image_files = image_files[:100]

print("Images selected for evaluation:", len(image_files))
print()

# ============================================================
# EVALUATION
# ============================================================

results = []

absolute_errors = []
percentage_errors = []
squared_errors = []

print("=" * 80)
print("MODEL EVALUATION")
print("=" * 80)

for index, image_path in enumerate(image_files, start=1):

    gt_path = GT_DIR / f"{image_path.stem}.txt"

    ground_truth = get_ground_truth(gt_path)

    image = cv2.imread(str(image_path))

    if image is None:
        print("Could not read:", image_path.name)
        continue

    predicted = predict_count(image)

    absolute_error = abs(predicted - ground_truth)

    if ground_truth > 0:
        percentage_error = (
            absolute_error / ground_truth
        ) * 100
    else:
        percentage_error = 0

    squared_error = (
        predicted - ground_truth
    ) ** 2

    absolute_errors.append(absolute_error)
    percentage_errors.append(percentage_error)
    squared_errors.append(squared_error)

    results.append([
        image_path.name,
        ground_truth,
        predicted,
        absolute_error,
        percentage_error
    ])

    print(
        f"{index:03d}/{len(image_files)} | "
        f"{image_path.name:12s} | "
        f"GT={ground_truth:5d} | "
        f"Pred={predicted:5d} | "
        f"Error={absolute_error:5d} | "
        f"Error%={percentage_error:7.2f}%"
    )


# ============================================================
# FINAL METRICS
# ============================================================

if len(absolute_errors) > 0:

    mae = np.mean(absolute_errors)

    rmse = math.sqrt(
        np.mean(squared_errors)
    )

    mape = np.mean(
        percentage_errors
    )

else:

    mae = 0
    rmse = 0
    mape = 0


print()
print("=" * 80)
print("FINAL RESULTS")
print("=" * 80)

print(f"Images evaluated : {len(results)}")
print(f"MAE              : {mae:.2f}")
print(f"RMSE             : {rmse:.2f}")
print(f"MAPE             : {mape:.2f}%")

print("=" * 80)


# ============================================================
# SAVE CSV
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True
)

with open(
    OUTPUT_CSV,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "image",
        "ground_truth",
        "predicted",
        "absolute_error",
        "percentage_error"
    ])

    writer.writerows(results)

print()
print("CSV saved to:")
print(OUTPUT_CSV)