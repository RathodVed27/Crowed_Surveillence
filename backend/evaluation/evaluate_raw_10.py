import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO


# ============================================================
# CONFIG
# ============================================================

MODEL_PATH = Path(
    r"F:\Crowed_Surveillence\runs\crowd_yolov8m_combined_tiled\weights\best.pt"
)

IMAGE_DIR = Path(
    r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0\val\images"
)

OUTPUT_DIR = Path(
    r"F:\Crowed_Surveillence\runs\raw_10_results"
)

TILE_SIZE = 512
OVERLAP = 128
STRIDE = TILE_SIZE - OVERLAP

CONFIDENCE = 0.03
IOU_MODEL = 0.50
MAX_DET = 1000

IMAGE_NAMES = [
    "0003",
    "0007",
    "0009",
    "0011",
    "0013",
    "0042",
    "0056",
    "0058",
    "0068",
    "0070",
]


# ============================================================
# GROUND TRUTH
# ============================================================

GROUND_TRUTH = {
    "0003": 804,
    "0007": 41,
    "0009": 26,
    "0011": 31,
    "0013": 5000,
    "0042": 40,
    "0056": 1371,
    "0058": 35,
    "0068": 96,
    "0070": 32,
}


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model...")

model = YOLO(str(MODEL_PATH))

print("Model loaded.")


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# PROCESS ONE IMAGE
# ============================================================

def process_image(image_name):

    image_path = IMAGE_DIR / f"{image_name}.jpg"

    image = cv2.imread(str(image_path))

    if image is None:
        print(f"ERROR: Could not read {image_path}")
        return None

    height, width = image.shape[:2]

    # --------------------------------------------------------
    # Tile positions
    # --------------------------------------------------------

    x_positions = list(
        range(
            0,
            max(1, width - TILE_SIZE + 1),
            STRIDE
        )
    )

    y_positions = list(
        range(
            0,
            max(1, height - TILE_SIZE + 1),
            STRIDE
        )
    )

    # Make sure right/bottom edges are covered.
    if width > TILE_SIZE:
        last_x = width - TILE_SIZE

        if last_x not in x_positions:
            x_positions.append(last_x)

    if height > TILE_SIZE:
        last_y = height - TILE_SIZE

        if last_y not in y_positions:
            y_positions.append(last_y)

    x_positions = sorted(set(x_positions))
    y_positions = sorted(set(y_positions))

    # --------------------------------------------------------
    # RAW detections
    # --------------------------------------------------------

    raw_count = 0

    for y in y_positions:

        for x in x_positions:

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
                iou=IOU_MODEL,
                max_det=MAX_DET,
                verbose=False,
                device=0
            )

            result = results[0]

            if result.boxes is None:
                continue

            classes = result.boxes.cls.cpu().numpy()

            # Class 0 = head
            for cls in classes:

                if int(cls) == 0:
                    raw_count += 1

    return raw_count


# ============================================================
# RUN EVALUATION
# ============================================================

results_table = []

print()
print("=" * 70)
print("RAW DETECTION BASELINE")
print("=" * 70)

for image_name in IMAGE_NAMES:

    gt = GROUND_TRUTH[image_name]

    print()
    print(f"Processing {image_name}...")
    print(f"Ground truth: {gt}")

    raw_count = process_image(image_name)

    if raw_count is None:
        continue

    error = raw_count - gt
    absolute_error = abs(error)

    percentage_error = (
        absolute_error / gt
    ) * 100

    results_table.append({
        "image": image_name,
        "ground_truth": gt,
        "raw_detection": raw_count,
        "error": error,
        "absolute_error": absolute_error,
        "percentage_error": percentage_error
    })

    print(f"Raw detections: {raw_count}")
    print(f"Error: {error:+d}")
    print(f"Absolute error: {absolute_error}")
    print(f"Percentage error: {percentage_error:.2f}%")


# ============================================================
# SUMMARY
# ============================================================

if not results_table:
    raise RuntimeError("No results generated.")


mae = np.mean([
    row["absolute_error"]
    for row in results_table
])

rmse = np.sqrt(
    np.mean([
        row["error"] ** 2
        for row in results_table
    ])
)

mape = np.mean([
    row["percentage_error"]
    for row in results_table
])


print()
print("=" * 70)
print("FINAL RESULTS")
print("=" * 70)

print()

print(
    f"{'Image':<10}"
    f"{'GT':>8}"
    f"{'Raw':>10}"
    f"{'Error':>10}"
    f"{'Abs Error':>12}"
    f"{'Error %':>12}"
)

print("-" * 70)

for row in results_table:

    print(
        f"{row['image']:<10}"
        f"{row['ground_truth']:>8}"
        f"{row['raw_detection']:>10}"
        f"{row['error']:>+10}"
        f"{row['absolute_error']:>12}"
        f"{row['percentage_error']:>11.2f}%"
    )

print("-" * 70)

print(f"MAE  : {mae:.2f}")
print(f"RMSE : {rmse:.2f}")
print(f"MAPE : {mape:.2f}%")


# ============================================================
# SAVE CSV
# ============================================================

csv_path = OUTPUT_DIR / "raw_10_results.csv"

with open(
    csv_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "image,ground_truth,raw_detection,"
        "error,absolute_error,percentage_error\n"
    )

    for row in results_table:

        f.write(
            f"{row['image']},"
            f"{row['ground_truth']},"
            f"{row['raw_detection']},"
            f"{row['error']},"
            f"{row['absolute_error']},"
            f"{row['percentage_error']:.2f}\n"
        )

print()
print(f"CSV saved to:")
print(csv_path)