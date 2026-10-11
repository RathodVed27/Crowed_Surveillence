from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

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

# Test representative images
IMAGE_NAMES = [
    "0003.jpg",   # 804
    "0007.jpg",   # 41
    "0009.jpg",   # 26
    "0011.jpg",   # 31
    "0013.jpg",   # 5000
    "0042.jpg",   # 40
    "0056.jpg",   # 1371
    "0058.jpg",   # 35
    "0068.jpg",   # 96
    "0070.jpg",   # 32
]

# Confidence thresholds
CONFIDENCES = [
    0.01,
    0.02,
    0.03,
    0.04,
    0.05,
    0.06,
    0.07,
    0.08,
    0.09,
    0.10,
]

TILE_SIZE = 512
OVERLAP = 128

MODEL_IOU = 0.50
FINAL_IOU = 0.50
MAX_DETECTIONS = 1000


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(MODEL_PATH)

print("Model loaded.")


# ============================================================
# GROUND TRUTH
# ============================================================

def get_ground_truth(gt_file):

    with open(gt_file, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f
            if line.strip()
        ]

    return len(lines)


# ============================================================
# TILED PREDICTION
# ============================================================

def predict_count(image, confidence):

    height, width = image.shape[:2]

    stride = TILE_SIZE - OVERLAP

    x_starts = list(range(0, width, stride))
    y_starts = list(range(0, height, stride))

    all_boxes = []
    all_scores = []

    for y in y_starts:

        for x in x_starts:

            x2 = min(x + TILE_SIZE, width)
            y2 = min(y + TILE_SIZE, height)

            tile = image[y:y2, x:x2]

            results = model.predict(
                source=tile,
                conf=confidence,
                iou=MODEL_IOU,
                imgsz=TILE_SIZE,
                max_det=MAX_DETECTIONS,
                device=0,
                verbose=False
            )

            result = results[0]

            if (
                result.boxes is None
                or len(result.boxes) == 0
            ):
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()

            for box, score in zip(boxes, scores):

                bx1, by1, bx2, by2 = box

                # Convert tile coordinates
                # to original image coordinates
                bx1 += x
                bx2 += x
                by1 += y
                by2 += y

                all_boxes.append(
                    [bx1, by1, bx2, by2]
                )

                all_scores.append(
                    float(score)
                )

    if len(all_boxes) == 0:
        return 0

    # --------------------------------------------------------
    # NMS
    # --------------------------------------------------------

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
        confidence,
        FINAL_IOU
    )

    if len(indices) == 0:
        return 0

    return len(indices)


# ============================================================
# RUN EVALUATION
# ============================================================

results_table = []

print()
print("=" * 80)
print("CROWD COUNT THRESHOLD EVALUATION")
print("=" * 80)


for image_name in IMAGE_NAMES:

    image_path = IMAGE_DIR / image_name
    gt_path = GT_DIR / f"{Path(image_name).stem}.txt"

    if not image_path.exists():
        print(f"Missing image: {image_name}")
        continue

    if not gt_path.exists():
        print(f"Missing GT: {gt_path}")
        continue

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"Cannot read: {image_path}")
        continue

    actual = get_ground_truth(gt_path)

    print()
    print(
        f"Image: {image_name} | "
        f"Ground truth: {actual}"
    )

    for confidence in CONFIDENCES:

        predicted = predict_count(
            image,
            confidence
        )

        error = abs(predicted - actual)

        if actual > 0:
            error_percent = (
                error / actual
            ) * 100
        else:
            error_percent = 0

        print(
            f"  conf={confidence:.2f} | "
            f"pred={predicted:5d} | "
            f"error={error:5d} | "
            f"error%={error_percent:7.2f}%"
        )

        results_table.append(
            {
                "image": image_name,
                "actual": actual,
                "confidence": confidence,
                "predicted": predicted,
                "error": error,
                "error_percent": error_percent
            }
        )


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 80)
print("AVERAGE ERROR BY CONFIDENCE")
print("=" * 80)

for confidence in CONFIDENCES:

    rows = [
        r
        for r in results_table
        if r["confidence"] == confidence
    ]

    if not rows:
        continue

    mean_error = np.mean(
        [r["error"] for r in rows]
    )

    mean_percent = np.mean(
        [r["error_percent"] for r in rows]
    )

    print(
        f"conf={confidence:.2f} | "
        f"mean absolute error={mean_error:.2f} | "
        f"mean percentage error={mean_percent:.2f}%"
    )


print()
print("=" * 80)
print("EVALUATION COMPLETE")
print("=" * 80)