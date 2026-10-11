from pathlib import Path
from PIL import Image
import shutil

# ============================================================
# JHU-CROWD++ → YOLO CONVERTER
# ============================================================

SOURCE = Path(r"F:\PROJECT DATASET\jhu_crowd_v2.0\jhu_crowd_v2.0")

OUTPUT = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetJHU")

# ------------------------------------------------------------
# Convert one split
# ------------------------------------------------------------

def convert_split(split):

    image_dir = SOURCE / split / "images"
    gt_dir = SOURCE / split / "gt"

    output_image_dir = OUTPUT / "images" / split
    output_label_dir = OUTPUT / "labels" / split

    output_image_dir.mkdir(parents=True, exist_ok=True)
    output_label_dir.mkdir(parents=True, exist_ok=True)

    image_files = list(image_dir.glob("*.jpg"))

    print()
    print("=" * 60)
    print(f"Processing: {split}")
    print(f"Images found: {len(image_files)}")
    print("=" * 60)

    converted = 0
    skipped = 0
    total_boxes = 0

    for index, image_path in enumerate(image_files, 1):

        gt_path = gt_dir / f"{image_path.stem}.txt"

        if not gt_path.exists():
            print(f"WARNING: Missing annotation: {gt_path.name}")
            skipped += 1
            continue

        try:
            # Read image dimensions
            with Image.open(image_path) as img:
                image_width, image_height = img.size

            yolo_lines = []

            with open(gt_path, "r", encoding="utf-8") as f:

                for line in f:

                    parts = line.strip().split()

                    if len(parts) < 4:
                        continue

                    # JHU annotation
                    x = float(parts[0])
                    y = float(parts[1])
                    w = float(parts[2])
                    h = float(parts[3])

                    # Convert top-left coordinates
                    # to YOLO center coordinates
                    center_x = x + w / 2
                    center_y = y + h / 2

                    # Normalize
                    center_x /= image_width
                    center_y /= image_height
                    w /= image_width
                    h /= image_height

                    # Class 0 = head
                    yolo_lines.append(
                        f"0 {center_x:.6f} {center_y:.6f} "
                        f"{w:.6f} {h:.6f}"
                    )

            # Copy image
            shutil.copy2(
                image_path,
                output_image_dir / image_path.name
            )

            # Save YOLO label
            output_label_path = (
                output_label_dir / f"{image_path.stem}.txt"
            )

            with open(output_label_path, "w", encoding="utf-8") as f:
                f.write("\n".join(yolo_lines))

            converted += 1
            total_boxes += len(yolo_lines)

            if index % 100 == 0:
                print(
                    f"Processed {index}/{len(image_files)} "
                    f"| Boxes: {total_boxes}"
                )

        except Exception as e:
            print(f"ERROR: {image_path.name} -> {e}")
            skipped += 1

    print()
    print(f"Finished {split}")
    print(f"Converted : {converted}")
    print(f"Skipped   : {skipped}")
    print(f"Head boxes: {total_boxes}")


# ------------------------------------------------------------
# Run conversion
# ------------------------------------------------------------

for split in ["train", "val", "test"]:
    if (SOURCE / split).exists():
        convert_split(split)

print()
print("=" * 60)
print("JHU-CROWD++ CONVERSION COMPLETE")
print("=" * 60)
print(f"Output: {OUTPUT}")