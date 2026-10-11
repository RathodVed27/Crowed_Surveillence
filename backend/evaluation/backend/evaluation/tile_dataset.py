from pathlib import Path
from PIL import Image

# ============================================================
# CONFIGURATION
# ============================================================

SOURCE = Path(r"F:\Crowed_Surveillence\backend\CrowdDataset")
OUTPUT = Path(r"F:\Crowed_Surveillence\backend\CrowdDatasetTiled")

TILE_SIZE = 512
OVERLAP = 128

# Keep an annotation if at least this much of the original
# bounding box remains inside the tile.
MIN_VISIBLE_RATIO = 0.30


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_positions(length, tile_size, overlap):
    """
    Generate tile start positions.

    Example:
    image width = 1024
    tile = 512
    overlap = 128

    positions will approximately be:
    0, 384, 512
    """

    stride = tile_size - overlap

    positions = []
    pos = 0

    while pos + tile_size < length:
        positions.append(pos)
        pos += stride

    # Always include the final tile so the complete image is covered.
    last = max(0, length - tile_size)

    if last not in positions:
        positions.append(last)

    return positions


def load_yolo_labels(label_path, image_width, image_height):
    """
    Read YOLO labels:

    class_id x_center y_center width height

    Convert normalized coordinates to pixel coordinates.
    """

    boxes = []

    if not label_path.exists():
        return boxes

    with open(label_path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()

            if len(parts) != 5:
                continue

            try:
                class_id = int(float(parts[0]))

                xc = float(parts[1]) * image_width
                yc = float(parts[2]) * image_height
                w = float(parts[3]) * image_width
                h = float(parts[4]) * image_height

                x1 = xc - w / 2
                y1 = yc - h / 2
                x2 = xc + w / 2
                y2 = yc + h / 2

                boxes.append(
                    {
                        "class_id": class_id,
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                    }
                )

            except ValueError:
                continue

    return boxes


def iou(box_a, box_b):
    """
    Calculate IoU between two boxes.
    """

    x1 = max(box_a[0], box_b[0])
    y1 = max(box_a[1], box_b[1])
    x2 = min(box_a[2], box_b[2])
    y2 = min(box_a[3], box_b[3])

    intersection_w = max(0, x2 - x1)
    intersection_h = max(0, y2 - y1)

    intersection = intersection_w * intersection_h

    area_a = max(0, box_a[2] - box_a[0]) * max(
        0, box_a[3] - box_a[1]
    )

    area_b = max(0, box_b[2] - box_b[0]) * max(
        0, box_b[3] - box_b[1]
    )

    union = area_a + area_b - intersection

    if union <= 0:
        return 0

    return intersection / union


def remove_duplicate_labels(labels):
    """
    Remove almost identical duplicate boxes created by
    the original annotation process.
    """

    cleaned = []

    for label in labels:

        duplicate = False

        for existing in cleaned:

            if label[0] != existing[0]:
                continue

            if iou(label[1:], existing[1:]) > 0.98:
                duplicate = True
                break

        if not duplicate:
            cleaned.append(label)

    return cleaned


# ============================================================
# PROCESS ONE SPLIT
# ============================================================

def process_split(split):
    print()
    print("=" * 60)
    print(f"Processing {split.upper()} dataset")
    print("=" * 60)

    source_images = SOURCE / "images" / split
    source_labels = SOURCE / "labels" / split

    output_images = OUTPUT / "images" / split
    output_labels = OUTPUT / "labels" / split

    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)

    image_files = []

    for extension in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
        image_files.extend(source_images.glob(extension))

    image_files = sorted(set(image_files))

    print(f"Found {len(image_files)} source images")

    total_tiles = 0
    total_labels = 0

    for image_index, image_path in enumerate(image_files, start=1):

        try:
            image = Image.open(image_path).convert("RGB")

        except Exception as e:
            print(f"ERROR opening {image_path.name}: {e}")
            continue

        width, height = image.size

        label_path = source_labels / f"{image_path.stem}.txt"

        boxes = load_yolo_labels(
            label_path,
            width,
            height
        )

        x_positions = get_positions(
            width,
            TILE_SIZE,
            OVERLAP
        )

        y_positions = get_positions(
            height,
            TILE_SIZE,
            OVERLAP
        )

        tile_number = 0

        for y in y_positions:

            for x in x_positions:

                # Actual tile boundaries
                tile_x1 = x
                tile_y1 = y
                tile_x2 = min(x + TILE_SIZE, width)
                tile_y2 = min(y + TILE_SIZE, height)

                tile_width = tile_x2 - tile_x1
                tile_height = tile_y2 - tile_y1

                # Create a 512x512 tile.
                tile = Image.new(
                    "RGB",
                    (TILE_SIZE, TILE_SIZE),
                    (0, 0, 0)
                )

                crop = image.crop(
                    (
                        tile_x1,
                        tile_y1,
                        tile_x2,
                        tile_y2
                    )
                )

                tile.paste(crop, (0, 0))

                tile_labels = []

                # ------------------------------------------------
                # Convert each original bounding box to tile coords
                # ------------------------------------------------

                for box in boxes:

                    bx1 = box["x1"]
                    by1 = box["y1"]
                    bx2 = box["x2"]
                    by2 = box["y2"]

                    # Find intersection with tile
                    ix1 = max(bx1, tile_x1)
                    iy1 = max(by1, tile_y1)

                    ix2 = min(bx2, tile_x2)
                    iy2 = min(by2, tile_y2)

                    intersection_w = max(0, ix2 - ix1)
                    intersection_h = max(0, iy2 - iy1)

                    intersection_area = (
                        intersection_w * intersection_h
                    )

                    original_area = max(
                        0,
                        bx2 - bx1
                    ) * max(
                        0,
                        by2 - by1
                    )

                    if original_area <= 0:
                        continue

                    visible_ratio = (
                        intersection_area /
                        original_area
                    )

                    # Ignore objects mostly outside the tile.
                    if visible_ratio < MIN_VISIBLE_RATIO:
                        continue

                    # Convert to tile coordinates.
                    new_x1 = ix1 - tile_x1
                    new_y1 = iy1 - tile_y1
                    new_x2 = ix2 - tile_x1
                    new_y2 = iy2 - tile_y1

                    # Clamp to tile.
                    new_x1 = max(0, min(TILE_SIZE, new_x1))
                    new_y1 = max(0, min(TILE_SIZE, new_y1))
                    new_x2 = max(0, min(TILE_SIZE, new_x2))
                    new_y2 = max(0, min(TILE_SIZE, new_y2))

                    new_width = new_x2 - new_x1
                    new_height = new_y2 - new_y1

                    if new_width <= 1 or new_height <= 1:
                        continue

                    # Convert back to YOLO normalized format.
                    new_x_center = (
                        (new_x1 + new_x2) / 2
                    ) / TILE_SIZE

                    new_y_center = (
                        (new_y1 + new_y2) / 2
                    ) / TILE_SIZE

                    new_w = new_width / TILE_SIZE
                    new_h = new_height / TILE_SIZE

                    tile_labels.append(
                        [
                            box["class_id"],
                            new_x_center,
                            new_y_center,
                            new_w,
                            new_h
                        ]
                    )

                # Remove duplicate labels.
                tile_labels = remove_duplicate_labels(
                    tile_labels
                )

                # ------------------------------------------------
                # Save tile
                # ------------------------------------------------

                tile_name = (
                    f"{image_path.stem}"
                    f"_tile_{tile_number:03d}.jpg"
                )

                tile_path = output_images / tile_name

                tile.save(
                    tile_path,
                    quality=95
                )

                # Save labels.
                label_output_path = (
                    output_labels /
                    f"{image_path.stem}"
                    f"_tile_{tile_number:03d}.txt"
                )

                with open(
                    label_output_path,
                    "w",
                    encoding="utf-8"
                ) as f:

                    for label in tile_labels:

                        class_id = label[0]
                        xc = label[1]
                        yc = label[2]
                        w = label[3]
                        h = label[4]

                        f.write(
                            f"{class_id} "
                            f"{xc:.6f} "
                            f"{yc:.6f} "
                            f"{w:.6f} "
                            f"{h:.6f}\n"
                        )

                total_tiles += 1
                total_labels += len(tile_labels)

                tile_number += 1

        if image_index % 25 == 0 or image_index == len(image_files):
            print(
                f"Processed {image_index}/{len(image_files)} "
                f"| Tiles: {total_tiles} "
                f"| Labels: {total_labels}"
            )

    print()
    print(f"Finished {split}")
    print(f"Total tiles: {total_tiles}")
    print(f"Total labels: {total_labels}")


# ============================================================
# CREATE DATASET YAML
# ============================================================

def create_yaml():

    yaml_path = OUTPUT / "dataset.yaml"

    yaml_content = f"""path: {OUTPUT.as_posix()}

train: images/train
val: images/val

nc: 1

names:
  0: head
"""

    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(yaml_content)

    print()
    print("=" * 60)
    print("dataset.yaml created")
    print(yaml_path)
    print("=" * 60)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SHANGHAITECH -> TILED YOLO DATASET")
    print("=" * 60)

    print(f"Source : {SOURCE}")
    print(f"Output : {OUTPUT}")
    print(f"Tile   : {TILE_SIZE}x{TILE_SIZE}")
    print(f"Overlap: {OVERLAP}")

    process_split("train")
    process_split("val")

    create_yaml()

    print()
    print("=" * 60)
    print("TILED DATASET CREATION COMPLETE")
    print("=" * 60)